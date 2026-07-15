import pytest

from src.ppo_v2_parquet_writer import (
    FASTPARQUET_FALLBACK,
    GOVERNED_PARQUET_PROFILE,
    INDEX_SERIALIZED,
    PANDAS_TO_PARQUET_ENGINE_AUTO,
    PARQUET_ENGINE,
    REMAINING_KWARGS,
    ParquetWriteAuthorizationError,
    build_governed_arrow_schema,
    write_governed_parquet,
)


def test_governed_pyarrow_writer_profile_is_exact_and_explicit():
    profile = GOVERNED_PARQUET_PROFILE
    assert PARQUET_ENGINE == "pyarrow"
    assert PANDAS_TO_PARQUET_ENGINE_AUTO == "PROHIBITED"
    assert FASTPARQUET_FALLBACK == "PROHIBITED"
    assert INDEX_SERIALIZED is False
    assert REMAINING_KWARGS == "PROHIBITED_UNLESS_EXPLICITLY_LISTED"
    assert profile.row_group_size == 65536
    assert profile.version == "2.6"
    assert profile.use_dictionary is False
    assert profile.compression == "snappy"
    assert profile.write_statistics is True
    assert profile.use_deprecated_int96_timestamps is False
    assert profile.allow_truncated_timestamps is False
    assert profile.data_page_version == "1.0"
    assert profile.store_schema is True
    assert profile.write_page_index is False
    assert profile.write_page_checksum is False
    assert profile.store_decimal_as_integer is False
    assert profile.write_time_adjusted_to_utc is False
    assert profile.use_compliant_nested_type is True


def test_writer_remains_inert_without_dataset_generation_authorization():
    with pytest.raises(ParquetWriteAuthorizationError):
        write_governed_parquet()


def test_explicit_arrow_schema_has_exact_nonnullable_contract():
    schema = build_governed_arrow_schema()
    assert len(schema) == 27
    assert schema.names[0:2] == ["Symbol", "Datetime"]
    assert all(field.nullable is False for field in schema)
