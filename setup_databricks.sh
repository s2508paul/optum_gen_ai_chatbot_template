#!/bin/bash

# Check if databricks-cli is installed
if ! command -v databricks &> /dev/null
then
    echo "databricks-cli could not be found"
    echo "Please install databricks-cli using the following command:"
    echo "pip install databricks-cli"
    exit
fi

# Sets variables
PROFILE=${1:-DEFAULT}
CATALOG=${2:-gen_ai}

# Loads the .env file
unamestr=$(uname)
if [ "$unamestr" = 'Linux' ]; then
  export $(grep -v '^#' .env | xargs -d '\n')
elif [ "$unamestr" = 'FreeBSD' ] || [ "$unamestr" = 'Darwin' ]; then
  export $(grep -v '^#' .env | xargs -0)
fi

# Create a default catalog
databricks --profile "$PROFILE" unity-catalog catalogs create --name "$CATALOG"

# Create schemas for the catalog
databricks --profile "$PROFILE" unity-catalog schemas create --catalog-name "$CATALOG" --name text_vectorized
databricks --profile "$PROFILE" unity-catalog schemas create --catalog-name "$CATALOG" --name operational
databricks --profile "$PROFILE" unity-catalog schemas create --catalog-name "$CATALOG" --name bot_answers

# Setup secrets for MSK
databricks secrets create-scope --scope msk
databricks secrets put --scope msk --key usr --string-value "$MSK_USR"
databricks secrets put --scope msk --key pass_key --string-value "$MSK_PASSKEY"

# Setup secrets for Open-AI
databricks --profile "$PROFILE" secrets create-scope --scope open_ai
databricks --profile "$PROFILE" secrets put --scope open_ai --key api_key --string-value "$OPEN_AI_API_KEY"

# Setup secrets for Pinecone
databricks --profile "$PROFILE" secrets create-scope --scope pinecone
databricks --profile "$PROFILE" secrets put --scope pinecone --key token --string-value "$PINECONE_TOKEN"
