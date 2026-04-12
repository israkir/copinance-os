"""Tiered narratives for aggregate options positioning.

Used by ``copinance_os.data.analytics.options.positioning`` (``build_options_positioning_dict``).
Intermediate strings match the historical default so fixtures stay stable when literacy is omitted.
See ``copinance_os.domain.literacy`` for shared primitives and job-context normalization.
"""

from __future__ import annotations

from copinance_os.domain.literacy import TieredCopy
from copinance_os.domain.models.profile import FinancialLiteracy

# --- Positioning block (main four signals) ---

_TC_CALL_OI_SHARE_NAME = TieredCopy(
    beginner="Calls as a share of all contracts",
    intermediate="Call Open Interest Share",
    advanced="Call OI share",
)
_TC_CALL_OI_SHARE_EXPL = TieredCopy(
    beginner=(
        "Out of all option contracts that are open, this is the fraction that are calls. "
        "A higher share often means more people are positioned for the stock to go up."
    ),
    intermediate=(
        "A larger share of call OI points to aggregate upside interest "
        "in the chain — sometimes consistent with sizable call interest, "
        "but not exclusive to any one player."
    ),
    advanced="Elevated call-OI share vs total OI: upside positioning in aggregate; not a named holder read.",
)

_TC_PUT_CALL_OI_NAME = TieredCopy(
    beginner="Puts compared to calls (open contracts)",
    intermediate="Put/Call OI Ratio",
    advanced="Put/call OI",
)
_TC_PUT_CALL_OI_EXPL = TieredCopy(
    beginner=(
        "This compares how many put contracts are open to how many call contracts are open. "
        "A higher number can mean more people are buying protection against a drop."
    ),
    intermediate="Elevated put/call OI can indicate hedging pressure or defensive positioning.",
    advanced="Put/call OI >1: defensive skew or hedging demand vs calls; contrarian read context-dependent.",
)

_TC_FLOW_CALLS_NAME = TieredCopy(
    beginner="Today’s trading: share that is calls",
    intermediate="Intraday Options Flow (Calls Share)",
    advanced="Volume: calls share",
)
_TC_FLOW_CALLS_EXPL = TieredCopy(
    beginner=(
        "Of all option trades today, this is the share that were call trades. "
        "More call trading can mean short-term optimism."
    ),
    intermediate="Call-heavy volume relative to puts may indicate bullish tactical flow.",
    advanced="Call-heavy tape vs puts: tactical flow skew; not positioning stock.",
)

_TC_GAMMA_TILT_NAME = TieredCopy(
    beginner="Gamma tilt (how call vs put sensitivity balances)",
    intermediate="Gamma Tilt",
    advanced="Gamma tilt",
)
_TC_GAMMA_TILT_EXPL = TieredCopy(
    beginner=(
        "Gamma measures how fast an option’s sensitivity to price moves changes. "
        "Here we compare that effect between calls and puts using open contracts."
    ),
    intermediate="Positive gamma tilt can support stabilization and upside continuation.",
    advanced="Net gamma tilt from OI-weighted chain gammas; stabilization vs convexity amplifier read.",
)

# --- Volatility ---

_TC_ATM_IV_NAME = TieredCopy(
    beginner="Expected price swings at the current stock price (nearest expiry)",
    intermediate="ATM Implied Volatility",
    advanced="ATM IV (near)",
)
_TC_ATM_IV_MAIN = TieredCopy(
    beginner=(
        "This is the market’s best guess of how much the stock might move, annualized, "
        "for options whose strike is closest to today’s price, for the nearest expiration date."
    ),
    intermediate=(
        "At-the-money implied volatility for the nearest listed expiration — "
        "the market’s baseline fear / demand for premium at spot."
    ),
    advanced="Near-tenor ATM IV: baseline vol level at spot; fear/greed proxy.",
)

_TC_IV_RANK_NAME = TieredCopy(
    beginner="How high today’s “expected swing” is vs this whole list",
    intermediate="Intra-Chain IV Rank",
    advanced="IV rank (chain)",
)
_TC_IV_RANK_MAIN = TieredCopy(
    beginner=(
        "If this number is high, today’s expected swing at the money is high compared with "
        "other strikes in the same snapshot (0 = lowest, 1 = highest)."
    ),
    intermediate=(
        "Percentile of ATM IV versus all implied volatilities observed in this chain snapshot "
        "(0 = lowest, 1 = highest)."
    ),
    advanced="ATM IV percentile vs chain IV sample; cross-sectional rank only.",
)
_TC_IV_RANK_NO_IV = TieredCopy(
    beginner="We could not rank swings because there is not enough volatility data in this list.",
    intermediate="IV rank unavailable without a usable volatility sample across the chain.",
    advanced="IV rank undefined: insufficient IV sample in snapshot.",
)
_TC_IV_INSUFFICIENT = TieredCopy(
    beginner="We do not have enough data here to estimate expected swings at the money.",
    intermediate="Insufficient chain or spot data to estimate ATM implied volatility.",
    advanced="ATM IV unavailable: chain/spot insufficient.",
)
_TC_IV_NO_QUOTES = TieredCopy(
    beginner="There is no usable “expected swing” number near the stock price for this date.",
    intermediate="No quoted implied volatility near the money for the nearest expiration.",
    advanced="No ATM IV quotes near spot for front expiry.",
)
_TC_IV_RANK_DEGENERATE = TieredCopy(
    beginner="How today’s at-the-money swing compares with all other swing numbers in this list.",
    intermediate="How current ATM IV ranks versus all IV prints in this chain snapshot.",
    advanced="ATM IV cross-sectional rank vs chain IV prints.",
)

_TC_VOL_COMBO_NAME = TieredCopy(
    beginner="At-the-money swing and its rank in this list",
    intermediate="ATM Implied Volatility · IV Rank",
    advanced="ATM IV · IV rank",
)

# --- Surface ---

_TC_SKEW_INSUFFICIENT = TieredCopy(
    beginner="We could not compare “similar-risk” puts and calls because delta numbers are missing.",
    intermediate="Not enough delta quotes to estimate 25-delta skew for the nearest expiration.",
    advanced="25Δ skew undefined: insufficient delta quotes.",
)
_TC_SKEW_OK = TieredCopy(
    beginner=(
        "We compare expected swings on a put and a call chosen to react similarly to small price moves. "
        "If puts look more “expensive” than calls, people may be paying extra for protection."
    ),
    intermediate=(
        "IV of the ~25-delta put minus the ~25-delta call (nearest expiry). "
        "Positive skew often reflects downside protection demand."
    ),
    advanced="25Δ risk-reversal skew (put IV − call IV, near); positive → downside protection bid.",
)
_TC_TERM_NEED_TWO = TieredCopy(
    beginner="We need two dates with good data to compare expected swings over time.",
    intermediate="Need two expirations with ATM IV to infer term structure.",
    advanced="Term structure undefined: need two ATM IV slices.",
)

_TC_SKEW_25D_NAME = TieredCopy(
    beginner="Put vs call “expensive” tilt (similar-risk options)",
    intermediate="25-Delta Skew",
    advanced="25Δ skew",
)
_TC_TERM_STRUCTURE_NAME = TieredCopy(
    beginner="How expected swings compare across dates",
    intermediate="Term Structure",
    advanced="IV term structure",
)

# --- Flow ---

_TC_UNUSUAL_NAME = TieredCopy(
    beginner="Unusual trading score",
    intermediate="Unusual Activity Score",
    advanced="Unusual activity score",
)

_TC_AGG_VOL_OI_NAME = TieredCopy(
    beginner="All trading today vs all open contracts",
    intermediate="Aggregate Volume / OI",
    advanced="Agg vol / OI",
)
_TC_AGG_VOL_OI_EXPL = TieredCopy(
    beginner=(
        "This divides all option trades today by all contracts still open. A higher number can "
        "mean more people are actively trading compared with positions that are just sitting there."
    ),
    intermediate=(
        "Total options volume divided by total open interest — higher values can "
        "indicate more tactical trading versus stuck inventory."
    ),
    advanced="Chain vol/OI: turnover vs inventory; tactical flow proxy.",
)

# --- Gamma ---

_TC_NET_GAMMA_EXPL = TieredCopy(
    beginner=(
        "This adds up how much “speed of change” exposure calls have, minus puts, using open "
        "contracts and today’s stock price. It is a rough picture, not a precise bank report."
    ),
    intermediate="Sum of gamma × OI × 100 × spot for calls minus puts — a coarse dealer-gamma proxy.",
    advanced="Dealer-gamma proxy: Σ(call γ·OI·100·S) − Σ(put γ·OI·100·S); sign = net inventory convexity.",
)
_TC_NET_GAMMA_NAME = TieredCopy(
    beginner="Net “speed-of-change” exposure (calls minus puts)",
    intermediate="Net Gamma Exposure",
    advanced="Net gamma (OI-weighted)",
)
_TC_GAMMA_REGIME_NAME = TieredCopy(
    beginner="Gamma regime (stabilizing vs amplifying)",
    intermediate="Gamma Regime",
    advanced="Gamma regime",
)
_TC_GAMMA_NEUTRAL = TieredCopy(
    beginner="Gamma effects look tiny in this snapshot, so we label the regime neutral.",
    intermediate="Gamma exposure is negligible in this snapshot — regime is effectively neutral.",
    advanced="Net |γ·OI| negligible → neutral gamma regime.",
)
_TC_GAMMA_POS = TieredCopy(
    beginner=(
        "If this pattern held, option dealers might tend to lean against big price spikes and dips, "
        "which can calm day-to-day moves."
    ),
    intermediate=(
        "Net gamma is positive — dealers are more likely to stabilize moves "
        "(fade extremes) if this positioning persists."
    ),
    advanced="Net dealer gamma >0: stabilization / mean-reversion pressure if inventory persists.",
)
_TC_GAMMA_NEG = TieredCopy(
    beginner="If this pattern held, option hedging could sometimes add fuel to strong trends.",
    intermediate=(
        "Net gamma is negative — convexity can amplify moves as hedgers chase delta "
        "in trending conditions."
    ),
    advanced="Net dealer gamma <0: convexity supply; trend amplification risk under chase.",
)
_TC_GAMMA_BAL = TieredCopy(
    beginner="Calls and puts balance out so we do not label a strong stabilizing or amplifying regime.",
    intermediate="Gamma is balanced — neither strong stabilization nor strong convexity amplification.",
    advanced="Balanced net gamma: no dominant stabilization vs convexity regime.",
)

# --- Structure ---

_TC_MAX_PAIN_NAME = TieredCopy(
    beginner="Price where option payouts might be lowest (simple story)",
    intermediate="Max Pain Strike",
    advanced="Max pain (nearest)",
)
_TC_MAX_PAIN_EXPL = TieredCopy(
    beginner=(
        "This is the price, for the nearest date, where total option payouts if the stock closed "
        "there would be as small as possible in this simple model. It is a common story people tell; "
        "it is not a forecast."
    ),
    intermediate=(
        "Strike that minimizes total intrinsic value paid to option holders at expiration "
        "(nearest expiry only) — a common magnet narrative, not a forecast."
    ),
    advanced="Nearest-expiry max-pain strike (intrinsic minimizer); narrative magnet, not a forecast.",
)

_TC_STRIKE_MAGNETS_NAME = TieredCopy(
    beginner="Prices where the most contracts are open (nearest date)",
    intermediate="Strike Magnets (OI)",
    advanced="OI magnets (near)",
)
_TC_STRIKE_MAGNETS_EXPL = TieredCopy(
    beginner=(
        "These are the stock prices where the largest number of option contracts are open for the "
        "nearest date — places traders often watch."
    ),
    intermediate="Largest open-interest strikes in the nearest expiration — where inventory tends to cluster.",
    advanced="Top OI strikes (front expiry): inventory clustering / potential pin context.",
)

_TC_IMPL_MOVE_NAME = TieredCopy(
    beginner="Rough “expected one-day move” from option prices (nearest date)",
    intermediate="Implied Move (Straddle)",
    advanced="Implied move (ATM straddle)",
)
_TC_IMPL_MOVE_EXPL = TieredCopy(
    beginner=(
        "We average the prices of the nearest call and put at the stock price, add them, and "
        "compare to the stock price to get a simple percent move people talk about."
    ),
    intermediate=(
        "ATM straddle mid / spot for the nearest expiration — a rough implied one-standard-deviation "
        "range proxy."
    ),
    advanced="ATM straddle mid / spot (near): crude implied move proxy; not a realized vol forecast.",
)


def analyst_summary(
    symbol: str, bias: str, confidence: float, window: str, lit: FinancialLiteracy
) -> str:
    horizon_b = "the next week or two" if window == "near" else "the next month or two"
    horizon_i = "next 1-2 weeks" if window == "near" else "next 1-2 months"
    horizon_a = "front slice" if window == "near" else "mid horizon"

    if bias == "bullish":
        tone_b = (
            f"For {symbol}, more option contracts and trading lean toward people expecting the "
            "price to rise than fall, when you add up the whole list of strikes. "
            "That is a big-picture picture of the market, not a story about one investor."
        )
        tone_i = "the aggregate options surface leans bullish — more call-heavy OI and flow"
        tone_a = "aggregate positioning reads call-heavy on OI and flow; surface bias bullish"
    elif bias == "bearish":
        tone_b = (
            f"For {symbol}, more option activity points to people protecting against a drop "
            "or betting on a drop, when you look at the whole chain together."
        )
        tone_i = (
            "the aggregate options surface leans bearish — more defensive put weight "
            "or softer call demand"
        )
        tone_a = "surface skews defensive: put weight or weak call demand dominates aggregates"
    else:
        tone_b = (
            f"For {symbol}, the mix of call and put contracts does not clearly favor one direction "
            "in this snapshot."
        )
        tone_i = "the options surface is mixed — no strong one-sided aggregate skew yet"
        tone_a = "no clear one-sided aggregate skew; balanced positioning reads"

    tail_b = (
        f" We do not name specific funds. This read is about {confidence * 100:.0f}% confident "
        f"for {horizon_b}, in plain language."
    )
    tail_i = (
        " That reflects overall market positioning in the chain, "
        "not a specific actor; heavy clusters can sometimes line up with large books, "
        "but we do not label institutions. "
        f"Model confidence is {confidence * 100:.0f}% for the {horizon_i} horizon."
    )
    tail_a = f" Confidence {confidence:.2f} ({horizon_a}); clusters are inventory, not named flow."

    if lit == FinancialLiteracy.BEGINNER:
        return tone_b + tail_b
    if lit == FinancialLiteracy.ADVANCED:
        return f"{symbol}: {tone_a}.{tail_a}"
    return f"For {symbol}, {tone_i}.{tail_i}"


def scenario_narratives(symbol: str, lit: FinancialLiteracy) -> tuple[str, str, str]:
    bull = TieredCopy(
        beginner=(
            f"If {symbol} stays above the price levels where a lot of contracts sit, the uptrend "
            "could continue."
        ),
        intermediate=f"Upside continuation if {symbol} holds above option-supported levels.",
        advanced=(
            f"Continuation bias if spot holds above OI clusters / short-gamma strikes in {symbol}."
        ),
    )
    bear = TieredCopy(
        beginner=(
            f"If more people buy protection or unwind bullish trades, {symbol} could see more "
            "downward pressure."
        ),
        intermediate=f"Downside pressure if hedging demand rises and calls unwind in {symbol}.",
        advanced=f"Drawdown risk if hedging lifts and call inventory unwinds in {symbol}.",
    )
    range_tc = TieredCopy(
        beginner="Prices may bounce in a range if buyers and sellers stay evenly matched.",
        intermediate="Mean-reverting regime likely if neither side gains flow dominance.",
        advanced="Range regime if flow does not break to one side; gamma pin possible.",
    )
    return bull.pick(lit), bear.pick(lit), range_tc.pick(lit)


def name_call_oi_share(lit: FinancialLiteracy) -> str:
    return _TC_CALL_OI_SHARE_NAME.pick(lit)


def expl_call_oi_share(lit: FinancialLiteracy) -> str:
    return _TC_CALL_OI_SHARE_EXPL.pick(lit)


def name_put_call_oi(lit: FinancialLiteracy) -> str:
    return _TC_PUT_CALL_OI_NAME.pick(lit)


def expl_put_call_oi(lit: FinancialLiteracy) -> str:
    return _TC_PUT_CALL_OI_EXPL.pick(lit)


def name_flow_calls_share(lit: FinancialLiteracy) -> str:
    return _TC_FLOW_CALLS_NAME.pick(lit)


def expl_flow_calls_share(lit: FinancialLiteracy) -> str:
    return _TC_FLOW_CALLS_EXPL.pick(lit)


def name_gamma_tilt(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_TILT_NAME.pick(lit)


def expl_gamma_tilt(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_TILT_EXPL.pick(lit)


def name_atm_iv(lit: FinancialLiteracy) -> str:
    return _TC_ATM_IV_NAME.pick(lit)


def expl_atm_iv_main(lit: FinancialLiteracy) -> str:
    return _TC_ATM_IV_MAIN.pick(lit)


def name_iv_rank(lit: FinancialLiteracy) -> str:
    return _TC_IV_RANK_NAME.pick(lit)


def expl_iv_rank_main(lit: FinancialLiteracy) -> str:
    return _TC_IV_RANK_MAIN.pick(lit)


def expl_iv_rank_no_iv(lit: FinancialLiteracy) -> str:
    return _TC_IV_RANK_NO_IV.pick(lit)


def expl_iv_insufficient(lit: FinancialLiteracy) -> str:
    return _TC_IV_INSUFFICIENT.pick(lit)


def expl_iv_no_quotes_near_money(lit: FinancialLiteracy) -> str:
    return _TC_IV_NO_QUOTES.pick(lit)


def expl_iv_rank_degenerate(lit: FinancialLiteracy) -> str:
    return _TC_IV_RANK_DEGENERATE.pick(lit)


def name_vol_combo_atm_iv_rank(lit: FinancialLiteracy) -> str:
    return _TC_VOL_COMBO_NAME.pick(lit)


def expl_vol_combo(lit: FinancialLiteracy, atm_val: float, iv_rank_val: float) -> str:
    return TieredCopy(
        beginner=(
            f"The market’s “expected swing” at the stock price is about {atm_val:.2f} percent per year "
            f"(shown as a percent number). Compared with all other strikes here, that ranks about "
            f"{iv_rank_val:.0%} of the way from lowest to highest."
        ),
        intermediate=(
            f"ATM IV is {atm_val:.2f}% (percentage points). "
            f"Intra-chain IV rank {iv_rank_val:.0%} — how that ATM print ranks versus "
            f"all implied volatilities in this snapshot."
        ),
        advanced=(
            f"ATM IV {atm_val:.2f}%; intra-chain IV rank {iv_rank_val:.0%} vs snapshot IV sample."
        ),
    ).pick(lit)


def expl_skew_insufficient(lit: FinancialLiteracy) -> str:
    return _TC_SKEW_INSUFFICIENT.pick(lit)


def expl_skew_ok(lit: FinancialLiteracy) -> str:
    return _TC_SKEW_OK.pick(lit)


def expl_term_need_two(lit: FinancialLiteracy) -> str:
    return _TC_TERM_NEED_TWO.pick(lit)


def name_skew_25d(lit: FinancialLiteracy) -> str:
    return _TC_SKEW_25D_NAME.pick(lit)


def name_term_structure(lit: FinancialLiteracy) -> str:
    return _TC_TERM_STRUCTURE_NAME.pick(lit)


def expl_term_move(lit: FinancialLiteracy, near: float, far: float, slope: str) -> str:
    label_b = slope.replace("_", " ")
    return TieredCopy(
        beginner=(
            f"Expected swings at the stock price go from about {near:.1f}% to about {far:.1f}% "
            f"when you move to the next date we can compare — that pattern is called {label_b} here."
        ),
        intermediate=f"ATM IV moves from {near:.1f}% (near) to {far:.1f}% (next slice) — {label_b}.",
        advanced=f"ATM IV {near:.1f}% → {far:.1f}% (next); {slope}.",
    ).pick(lit)


def name_unusual_activity(lit: FinancialLiteracy) -> str:
    return _TC_UNUSUAL_NAME.pick(lit)


def expl_unusual_activity(lit: FinancialLiteracy, vol_threshold: int) -> str:
    return TieredCopy(
        beginner=(
            f"We count places where today’s trading is unusually high compared with contracts still open "
            f"(more than twice as much trading as open contracts, and more than {vol_threshold} trades), "
            "then turn that into a 0–100 style score."
        ),
        intermediate=(
            f"Counts strikes where volume is elevated versus open interest (ratio > 2, "
            f"volume > {vol_threshold}), scaled into a 0–100-style intensity score."
        ),
        advanced=(
            f"Heuristic unusual-activity score: vol/OI>2 & vol>{vol_threshold} strikes, scaled 0–100."
        ),
    ).pick(lit)


def name_agg_vol_oi(lit: FinancialLiteracy) -> str:
    return _TC_AGG_VOL_OI_NAME.pick(lit)


def expl_agg_vol_oi(lit: FinancialLiteracy) -> str:
    return _TC_AGG_VOL_OI_EXPL.pick(lit)


def expl_net_gamma(lit: FinancialLiteracy) -> str:
    return _TC_NET_GAMMA_EXPL.pick(lit)


def name_net_gamma(lit: FinancialLiteracy) -> str:
    return _TC_NET_GAMMA_NAME.pick(lit)


def name_gamma_regime(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_REGIME_NAME.pick(lit)


def expl_gamma_neutral_flat(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_NEUTRAL.pick(lit)


def expl_gamma_positive(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_POS.pick(lit)


def expl_gamma_negative(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_NEG.pick(lit)


def expl_gamma_balanced(lit: FinancialLiteracy) -> str:
    return _TC_GAMMA_BAL.pick(lit)


def name_max_pain(lit: FinancialLiteracy) -> str:
    return _TC_MAX_PAIN_NAME.pick(lit)


def expl_max_pain(lit: FinancialLiteracy) -> str:
    return _TC_MAX_PAIN_EXPL.pick(lit)


def name_strike_magnets(lit: FinancialLiteracy) -> str:
    return _TC_STRIKE_MAGNETS_NAME.pick(lit)


def expl_strike_magnets(lit: FinancialLiteracy) -> str:
    return _TC_STRIKE_MAGNETS_EXPL.pick(lit)


def name_implied_move(lit: FinancialLiteracy) -> str:
    return _TC_IMPL_MOVE_NAME.pick(lit)


def expl_implied_move(lit: FinancialLiteracy) -> str:
    return _TC_IMPL_MOVE_EXPL.pick(lit)
