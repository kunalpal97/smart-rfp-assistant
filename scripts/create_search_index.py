
"""Create the Azure AI Search index for Smart RFP Assistant."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

# Ensure imports work when running from scripts/.
BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(BACKEND_ROOT / ".env")

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
api_key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv(
    "AZURE_SEARCH_INDEX_NAME",
    "rfp-chunks-v1",
)

if not endpoint or not api_key:
    raise SystemExit(
        "Missing AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY."
    )

VECTOR_DIMENSIONS = 3072

client = SearchIndexClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key),
)

# Never overwrite an existing index without reviewing its schema.
try:
    existing = client.get_index(index_name)
except ResourceNotFoundError:
    existing = None

if existing is not None:
    print(f"Index '{index_name}' already exists.")
    print("No changes made.")
    raise SystemExit(0)

fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True,
    ),
    SimpleField(
        name="document_id",
        type=SearchFieldDataType.String,
        filterable=True,
    ),
    SearchableField(
        name="source_file",
        type=SearchFieldDataType.String,
    ),
    SimpleField(
        name="page",
        type=SearchFieldDataType.String,
        filterable=True,
    ),
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
    ),
    SimpleField(
        name="content_type",
        type=SearchFieldDataType.String,
        filterable=True,
        facetable=True,
    ),
    SimpleField(
        name="table_ids",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.String
        ),
        filterable=True,
    ),
    SimpleField(
        name="figure_ids",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.String
        ),
        filterable=True,
    ),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.Single
        ),
        searchable=True,
        vector_search_dimensions=VECTOR_DIMENSIONS,
        vector_search_profile_name="rfp-vector-profile",
        hidden=True,
    ),
]

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="rfp-hnsw",
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="rfp-vector-profile",
            algorithm_configuration_name="rfp-hnsw",
        )
    ],
)

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search,
)

client.create_index(index)

print("PASS: Azure AI Search index created.")
print("Index:", index_name)
print("Vector dimensions:", VECTOR_DIMENSIONS)
print("Fields:", [field.name for field in fields])
