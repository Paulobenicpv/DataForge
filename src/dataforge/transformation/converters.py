"""Conversoes de datas e numeros com precisao decimal."""
from decimal import Decimal, InvalidOperation
import re
import pandas as pd


def convert_series(values, rule):
    if rule["type"] == "date":
        return pd.to_datetime(
            values,
            format=rule["format"],
            errors="coerce",
        )

    decimal = rule.get("decimal", ".")
    thousands = rule.get("thousands")

    integer = r"[0-9]+"
    if thousands:
        separator = re.escape(thousands)
        integer = (
            rf"(?:[0-9]+|[0-9]{{1,3}}"
            rf"(?:{separator}[0-9]{{3}})+)"
        )

    fraction = re.escape(decimal)
    pattern = re.compile(
        rf"[+-]?(?:{integer}(?:{fraction}[0-9]*)?"
        rf"|{fraction}[0-9]+)(?:[eE][+-]?[0-9]+)?"
    )

    def parse(value):
        if pd.isna(value):
            return pd.NA

        value = str(value).strip()
        if not value or pattern.fullmatch(value) is None:
            return pd.NA

        normalized = (
            value.replace(thousands, "") if thousands else value
        )
        normalized = normalized.replace(decimal, ".")

        try:
            number = Decimal(normalized)
            return number if number.is_finite() else pd.NA
        except InvalidOperation:
            return pd.NA

    return values.map(parse).astype(object)
