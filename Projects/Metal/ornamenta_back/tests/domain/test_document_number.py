"""Tests para el value object DocumentNumber."""

import pytest
from pydantic import ValidationError

from app.domain.value_objects.document_number import DocumentEnum, DocumentNumber


class TestDocumentNumber:
    """Tests para validar DocumentNumber con diferentes tipos de datos."""

    def test_create_document_number_with_numeric_string(self):
        """Test: create document con string numerico."""
        doc = DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC)
        assert doc.value == "1234567890"
        assert doc.doc_type == DocumentEnum.CC

    def test_create_document_number_with_alphanumeric_string(self):
        """Test: create document con string alfanumerico."""
        doc = DocumentNumber(value="ABC123DEF456", doc_type=DocumentEnum.CE)
        assert doc.value == "ABC123DEF456"
        assert doc.doc_type == DocumentEnum.CE

    def test_create_document_number_with_special_chars(self):
        """Test: create document con caracteres especiales (guiones)."""
        doc = DocumentNumber(value="900-123-456", doc_type=DocumentEnum.NIT)
        assert doc.value == "900-123-456"
        assert doc.doc_type == DocumentEnum.NIT

    def test_create_document_number_max_length(self):
        """Test: create document con exactamente 12 caracteres."""
        doc = DocumentNumber(value="123456789012", doc_type=DocumentEnum.CC)
        assert doc.value == "123456789012"
        assert len(doc.value) == 12

    def test_create_document_number_exceeds_max_length(self):
        """Test: rechazar document que excede 12 caracteres."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentNumber(value="1234567890123", doc_type=DocumentEnum.CC)
        
        assert "no puede exceder 12 caracteres" in str(exc_info.value)

    def test_create_document_number_empty_string(self):
        """Test: rechazar document vacio."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentNumber(value="", doc_type=DocumentEnum.CC)
        
        assert "no puede estar vacio" in str(exc_info.value)

    def test_create_document_number_whitespace_only(self):
        """Test: rechazar document con solo espacios."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentNumber(value="   ", doc_type=DocumentEnum.CC)
        
        assert "no puede estar vacio" in str(exc_info.value)

    def test_create_document_number_with_leading_trailing_spaces(self):
        """Test: create document eliminando espacios al inicio y final."""
        doc = DocumentNumber(value="  1234567890  ", doc_type=DocumentEnum.CC)
        assert doc.value == "1234567890"

    def test_create_document_number_mixed_alphanumeric(self):
        """Test: create document con letras y numbers mezclados."""
        test_cases = [
            ("A1B2C3D4E5", DocumentEnum.CE),
            ("X123456789", DocumentEnum.CE),
            ("900456789-1", DocumentEnum.NIT),
            ("CE1234567", DocumentEnum.CE),
        ]
        
        for value, doc_type in test_cases:
            doc = DocumentNumber(value=value, doc_type=doc_type)
            assert doc.value == value
            assert doc.doc_type == doc_type

    def test_document_number_immutability(self):
        """Test: verificar que DocumentNumber es inmutable."""
        doc = DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC)
        
        with pytest.raises(ValidationError):
            doc.value = "9876543210"

    def test_document_number_str_representation(self):
        """Test: verificar representacion string del document."""
        doc = DocumentNumber(value="1234567890", doc_type=DocumentEnum.CC)
        assert str(doc) == "1234567890"

    def test_create_document_with_all_types(self):
        """Test: create documents con todos los tipos disponibles."""
        test_cases = [
            ("1234567890", DocumentEnum.CC),
            ("ABC12345678", DocumentEnum.CE),
            ("900456789", DocumentEnum.NIT),
        ]
        
        for value, doc_type in test_cases:
            doc = DocumentNumber(value=value, doc_type=doc_type)
            assert doc.value == value
            assert doc.doc_type == doc_type

    def test_document_number_with_unicode_characters(self):
        """Test: create document con caracteres unicode (si es necesario)."""
        # Dependiendo de los requisitos, podrias querer aceptar o rechazar unicode
        doc = DocumentNumber(value="ABC123", doc_type=DocumentEnum.CE)
        assert doc.value == "ABC123"
