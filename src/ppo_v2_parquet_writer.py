"""Governed PyArrow writer profile; dataset writing remains unauthorized."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.ppo_v2_data_contract import validate_output_path, validate_reconstructed_frame

PARQUET_ENGINE = "pyarrow"
PANDAS_TO_PARQUET_ENGINE_AUTO = "PROHIBITED"
FASTPARQUET_FALLBACK = "PROHIBITED"
INDEX_SERIALIZED = False
REMAINING_KWARGS = "PROHIBITED_UNLESS_EXPLICITLY_LISTED"


class ParquetWriteAuthorizationError(RuntimeError):
    """Raised because writing is outside this implementation checkpoint."""


@dataclass(frozen=True)
class GovernedParquetWriterProfile:
    row_group_size: int = 65536
    version: str = "2.6"
    use_dictionary: bool = False
    compression: str = "snappy"
    write_statistics: bool = True
    use_deprecated_int96_timestamps: bool = False
    coerce_timestamps: None = None
    allow_truncated_timestamps: bool = False
    data_page_size: None = None
    compression_level: None = None
    use_byte_stream_split: bool = False
    column_encoding: None = None
    data_page_version: str = "1.0"
    write_batch_size: None = None
    dictionary_pagesize_limit: None = None
    store_schema: bool = True
    write_page_index: bool = False
    write_page_checksum: bool = False
    sorting_columns: None = None
    store_decimal_as_integer: bool = False
    write_time_adjusted_to_utc: bool = False
    max_rows_per_page: None = None
    bloom_filter_options: None = None
    flavor: None = None
    filesystem: None = None
    use_compliant_nested_type: bool = True
    encryption_properties: None = None

    def pyarrow_options(self) -> dict[str, Any]:
        """Return only explicitly governed writer keywords."""

        return asdict(self)


GOVERNED_PARQUET_PROFILE = GovernedParquetWriterProfile()


def build_governed_arrow_schema() -> Any:
    """Build the explicit schema lazily without writing or selecting a fallback."""

    try:
        import pyarrow as pa
    except ImportError as exc:
        raise RuntimeError("pyarrow is required to build the governed schema") from exc

    from src.ppo_v2_data_contract import ENGINEERED_FEATURE_COLUMNS

    fields = [
        pa.field("Symbol", pa.string(), nullable=False),
        pa.field("Datetime", pa.timestamp("ns", tz="UTC"), nullable=False),
    ]
    fields.extend(
        pa.field(column, pa.float64(), nullable=False)
        for column in ("Open", "High", "Low", "Close", "Volume")
    )
    fields.extend(
        pa.field(column, pa.float64(), nullable=False)
        for column in ENGINEERED_FEATURE_COLUMNS
    )
    return pa.schema(fields)


def validate_write_intent(data: Any, output_path: str | Path) -> dict[str, Any]:
    """Validate a future write without touching the filesystem."""

    validate_output_path(output_path)
    validate_reconstructed_frame(data)
    return GOVERNED_PARQUET_PROFILE.pyarrow_options()


def write_governed_parquet(*_: object, **__: object) -> None:
    """Remain inert until dataset generation receives separate authorization."""

    raise ParquetWriteAuthorizationError("Parquet dataset writing is not authorized")
