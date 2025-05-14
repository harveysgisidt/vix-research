import pandas as pd
import numpy as np

class VIXCalculator:
    def __init__(self, df):
        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"], format="%Y%m%d")
        self.df["expr_date"] = pd.to_datetime(self.df["expr_date"], format="%Y%m%d")
        self.df["mid"] = (self.df["L_BID"] + self.df["L_ASK"]) / 2

    def calculate_for_date(self, date_str):
        """Check if the selected day has data."""
        date = pd.to_datetime(date_str)
        df_day = self.df[self.df["date"] == date]

        if df_day.empty:
            print(f"⚠️ No data found on {date_str}")
            return None

        print(f"✅ {len(df_day)} rows of data found for {date_str}")
        return df_day

    def get_near_next_terms(self, df_day):
        """Return the dates of near and next terms."""
        expr_dates = sorted(df_day["expr_date"].unique())
        if len(expr_dates) < 2:
            print("⚠️ The valid expiration date is less than 2.")
            return None, None

        near = expr_dates[0]
        next_ = expr_dates[1]
        print(f"📅 Near-term: {near.date()} / Next-term: {next_.date()}")
        return near, next_

    def compute_forward_and_K0(self, df_term, r, T):
        """Return F, K0 with the condition K0<F."""
        # filter calls and puts with bid > 0 and create a new column of mid-quoted price
        calls = df_term[(df_term["PC"] == 1) & (df_term["L_BID"] > 0)][["K", "mid"]].rename(columns={"mid": "call_mid"})
        puts = df_term[(df_term["PC"] == 2) & (df_term["L_BID"] > 0)][["K", "mid"]].rename(columns={"mid": "put_mid"})

        # merge calls and puts with
        merged = pd.merge(calls, puts, on="K")
        if merged.empty:
            print("❌ No paired Call/Put.")
            return None, None

        # extract the K0 (with smallest diff of call_mid and put_mid)
        merged["diff"] = abs(merged["call_mid"] - merged["put_mid"])
        min_row = merged.loc[merged["diff"].idxmin()]

        K0 = min_row["K"]
        F = K0 + np.exp(r * T) * (min_row["call_mid"] - min_row["put_mid"])

        # check K0 to make sure K0 < F
        if K0 > F:
            candidates = merged[merged["K"] < F]["K"]
            if not candidates.empty:
                K0 = candidates.max()

        print(f"🎯 Forward F = {F:.2f}, Adjusted K₀ = {K0}")
        return F, K0

    def calculate_squared_sigma(self, df_term, F, K0, T, r):
        """Return squared sigma."""
        df_term = df_term.copy()

        # OTM contract only
        calls_otm = df_term[(df_term["PC"] == 1) & (df_term["K"] > K0)].sort_values("K")
        puts_otm = df_term[(df_term["PC"] == 2) & (df_term["K"] < K0)].sort_values("K", ascending=False)
        atm = df_term[df_term["K"] == K0]

        # check condition that exclude data which has two consecutive 0 of bid price or volume.
        def stop_rule(df):
            rows = []
            zero_streak = 0
            for _,row in df.iterrows():
                if row["L_BID"] <= 0 or row["VOL"] == 0:
                    zero_streak += 1
                    if zero_streak >= 2:
                        break
                else:
                    zero_streak = 0
                    rows.append(row)
            return pd.DataFrame(rows)

        calls = stop_rule(calls_otm)
        puts = stop_rule(puts_otm)

        # concatenate the filtered options with sorted K
        full = pd.concat([puts, atm, calls]).sort_values("K").reset_index(drop=True)

        # compute ΔK
        Ks = full["K"].values
        delta_K = []
        for i in range(len(Ks)):
            if i == 0:
                dk = Ks[i + 1] - Ks[i]
            elif i == len(Ks) - 1:
                dk = Ks[i] - Ks[i - 1]
            else:
                dk = (Ks[i + 1] - Ks[i - 1]) / 2
            delta_K.append(dk)
        full["ΔK"] = delta_K

        # compute Q(K) and contrib
        full["Q"] = full["mid"]
        full["contrib"] = (full["ΔK"] / (full["K"] ** 2)) * np.exp(r * T) * full["Q"]

        # compute σ²
        squared_sigma = (2 / T) * full["contrib"].sum() - (1 / T) * ((F / K0 - 1) ** 2)

        return squared_sigma

    def calculate_vix(self, date_str):
        """Coalition of previous functions to compute and return final VIX."""
        # Check the date
        df_day = self.calculate_for_date(date_str)
        if df_day is None:
            return None

        # return the next two terms
        near, next_ = self.get_near_next_terms(df_day)
        if near is None or next_ is None:
            return None

        # extract the rows with the date of near and next term
        near_df = df_day[df_day["expr_date"] == near]
        next_df = df_day[df_day["expr_date"] == next_]

        # T, rf, N1, N2
        T_near = near_df["T"].iloc[0] / 365
        T_next = next_df["T"].iloc[0] / 365
        r_near = near_df["rf"].iloc[0] / 100
        r_next = next_df["rf"].iloc[0] / 100
        N1 = near_df["T"].iloc[0]
        N2 = next_df["T"].iloc[0]

        # Find F/K0 of two terms
        F_near, K0_near = self.compute_forward_and_K0(near_df, r_near, T_near)
        F_next, K0_next = self.compute_forward_and_K0(next_df, r_next, T_next)

        if F_near is None or F_next is None:
            print("❌ F/K₀ not found")
            return None

        # compute sigmas
        squared_sigma_near = self.calculate_squared_sigma(near_df, F_near, K0_near, T_near, r_near)
        squared_sigma_next = self.calculate_squared_sigma(next_df, F_next, K0_next, T_next, r_next)

        numerator = T_near * squared_sigma_near * (N2 - 30) + T_next * squared_sigma_next * (30 - N1)
        denominator = N2 - N1
        vix_squared = (numerator / denominator) * (365 / 30)
        vix = 100 * (vix_squared ** 0.5)

        print(f"📈 VIX on {date_str} = {vix:.2f}")
        return vix
