from pymongo import MongoClient, ASCENDING
from pymongo.encryption_options import AutoEncryptionOpts
from pymongo.encryption import ClientEncryption
import base64
import os
from bson.codec_options import CodecOptions
from bson.binary import STANDARD, UUID


# start-kmsproviders
provider = "kmip"
kms_providers = {provider: {"endpoint": "<endpoint for your KMIP KMS>"}}
# end-kmsproviders

# start-datakeyopts
master_key = (
    {}
)  # an empty key object prompts your KMIP provider to generate a new Customer Master Key
# end-datakeyopts

# start-create-index
connection_string = "<your connection string here>"

key_vault_coll = "__keyVault"
key_vault_db = "encryption"
key_vault_namespace = f"{key_vault_db}.{key_vault_coll}"
key_vault_client = MongoClient(connection_string)
# Drop the Key Vault Collection in case you created this collection
# in a previous run of this application.
key_vault_client.drop_database(key_vault_db)
# Drop the database storing your encrypted fields as all
# the DEKs encrypting those fields were deleted in the preceding line.
key_vault_client["medicalRecords"].drop_collection("patients")
key_vault_client[key_vault_db][key_vault_coll].create_index(
    [("keyAltNames", ASCENDING)],
    unique=True,
    partialFilterExpression={"keyAltNames": {"$exists": True}},
)
# end-create-index

# start-create-tls
tls_options = {
    "kmip": {
        "tlsCAFile": "<path to file containing your Certificate Authority certificate>",
        "tlsCertificateKeyFile": "<path to your client certificate file>",
    }
}
# end-create-tls

# start-create-dek
key_vault_database = "encryption"
key_vault_collection = "__keyVault"
key_vault_namespace = f"{key_vault_database}.{key_vault_collection}"

client = MongoClient(connection_string)
client_encryption = ClientEncryption(
    kms_providers,  # pass in the kms_providers variable from the previous step
    key_vault_namespace,
    client,
    CodecOptions(uuid_representation=STANDARD),
    kms_tls_options=tls_options,
)
data_key_id = client_encryption.create_data_key(provider, master_key)

base_64_data_key_id = base64.b64encode(data_key_id)
print("DataKeyId [base64]: ", base_64_data_key_id)
# end-create-dek
