from babel.numbers import format_decimal
from .event import Event 
import logging

# Example ISIN to ticker symbol mapping
ISIN_TO_TICKER = {
    "IE000RDRMSD1": "IEMB.L",   # Example ticker for ISIN IE000RDRMSD1
    "IE00B4L5Y983": "IWDA.L",   # Example ticker for Core MSCI World USD (Acc)
    "IE00B4L5YC18": "EIMI.L",   # Example ticker for ISIN IE00B4L5YC18
    "IE00B5BMR087": "HYLD.L",   # Example ticker for ISIN IE00B5BMR087
    "IE00BYZK4552": "CRBN.L",   # Example ticker for ISIN IE00BYZK4552
    "US0378331005": "AAPL",     # Apple Inc.
    "US5949181045": "MSFT",     # Microsoft Corporation
    "US5951121038": "MMM",      # 3M Company
    "US67066G1040": "NVDA",     # NVIDIA Corporation
    "US88160R1014": "TSLA",     # Tesla, Inc.
    "US91332U1016": "UNH",      # UnitedHealth Group Incorporated
    "XF000BTC0017": "BTC-USD",  # Bitcoin/USD
}

def export_yahoo_csv(timeline, output_path, lang="en"):
    """
    Export transactions in a CSV format compatible with Yahoo Finance.
    """

    log = logging.getLogger(__name__)

    with open(output_path, "w", encoding="utf-8") as f:
        csv_fmt = "{symbol},{trade_date},{purchase_price},{quantity}\n"
        header = '"Symbol","Trade Date","Purchase Price","Quantity"\n'
        f.write(header)

        for event_json in timeline:
            event = Event(event_json)
            if not event.is_pp_relevant:
                continue

            # Convert ISIN to ticker symbol
            symbol = ISIN_TO_TICKER.get(event.isin)
            if not symbol:  # Skip entries with no corresponding symbol
                log.warning(f"Skipping event due to missing symbol for ISIN: {event.isin}")
                continue

            # Skip if amount or shares are missing or empty
            if not event.amount or not event.shares:
                log.warning("Skipping event due to missing amount or shares")
                continue

            try:
                amount = float(event.amount)
                quantity = float(event.shares)
                purchase_price = amount / quantity
            except (TypeError, ValueError) as e:
                log.error(f"Skipping event due to error: {e}")
                continue  # Skip if amount or shares are invalid

            trade_date = event.date.replace("-", "")  # Remove dashes to get YYYYMMDD

            # Format the purchase price and quantity according to locale
            formatted_purchase_price = format_decimal(purchase_price, locale=lang)
            formatted_quantity = format_decimal(quantity, locale=lang)

            f.write(
                csv_fmt.format(
                    symbol=symbol,
                    trade_date=trade_date,
                    purchase_price=formatted_purchase_price,
                    quantity=formatted_quantity,
                )
            )

    log.info("Yahoo CSV creation finished!")
