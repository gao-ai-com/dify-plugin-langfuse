# Langfuse Plugin - Packaging, Signing & Installation Guide

This guide covers the complete process for packaging, signing, verifying, and installing the Langfuse plugin for Dify, including the necessary Dify daemon configuration.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Generate RSA Key Pair](#step-1-generate-rsa-key-pair)
- [Step 2: Package the Plugin](#step-2-package-the-plugin)
- [Step 3: Sign the Plugin Package](#step-3-sign-the-plugin-package)
- [Step 4: Verify the Signature](#step-4-verify-the-signature)
- [Step 5: Configure Dify Daemon](#step-5-configure-dify-daemon)
- [Step 6: Install via Dify UI](#step-6-install-via-dify-ui)
- [Step 7: Configure Langfuse Credentials](#step-7-configure-langfuse-credentials)

---

## Prerequisites

Before you begin, ensure you have:

- **Dify CLI** installed ([Installation Guide](https://docs.dify.ai/en/develop-plugin/cli))

```bash
# Verify Dify CLI installation
dify --version

# Clone the plugin repository
git clone https://github.com/Attraqt/dify-plugin-langfuse.git
cd dify-plugin-langfuse
```

---

## Step 1: Generate RSA Key Pair

Generate a cryptographic key pair for signing your plugin:

```bash
# Generate the key pair
dify signature generate -f langf-plugin-kp
```

**Output:**
```
✓ Key pair generated successfully
  Private key: langf-plugin-kp.private.pem
  Public key: langf-plugin-kp.public.pem
```

**⚠️ Security Warning:**
- **NEVER** commit `langf-plugin-kp.private.pem` to version control
- Store the private key in a secure location (e.g., AWS Secrets Manager, HashiCorp Vault)
- Only the public key (`langf-plugin-kp.public.pem`) should be shared with your Dify deployment

```bash
# Add private key to .gitignore
echo "*.private.pem" >> .gitignore
echo "langf-plugin-kp.private.pem" >> .gitignore
```

---

## Step 2: Package the Plugin

Create a `.difypkg` package file from the plugin source:

```bash
# Package the plugin
dify plugin package . -o langf-plugin-pkg.difypkg
```

**Output:**
```
✓ Plugin packaged successfully
  Output path: langf-plugin-pkg.difypkg
```

The package includes:
- Plugin manifest (`manifest.yaml`)
- Provider definitions (`provider/langfuse.yaml`)
- Tool implementations (`tools/*.yaml` and Python files)
- Assets (icons, documentation)
- Dependencies (`requirements.txt`)

---

## Step 3: Sign the Plugin Package

Apply a digital signature to the package using your private key:

```bash
# Sign the package
dify signature sign langf-plugin-pkg.difypkg -p langf-plugin-kp.private.pem
```

**Output:**
```
✓ Plugin signed successfully
  Output path: langf-plugin-pkg.signed.difypkg
```

This creates a signed package that includes:
- The original plugin package
- A cryptographic signature
- Metadata for verification

---

## Step 4: Verify the Signature

Confirm the signature is valid before deployment:

```bash
# Verify the signature
dify signature verify langf-plugin-pkg.signed.difypkg -p langf-plugin-kp.public.pem
```

**Output:**
```
✓ Plugin verified successfully
```

**Note:** Without the `-p` parameter, verification uses the Dify Marketplace public key, which will fail for third-party plugins.

---

## Step 5: Configure Dify Daemon

To enable third-party plugin verification, configure your Dify deployment with the public key.

### For Helm Deployments

Added to  `pluginDaemon`:

```yaml
extraEnv:
   - name: FORCE_VERIFYING_SIGNATURE
      value: "false"
   - name: THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED
      value: "true"
```
Added to `dify-dev`:

```yaml
persistence:
   enabled: true
   mountPath: /app/storage
   persistentVolumeClaim:
      storageClass: gp2
      size: 1Gi
```

Update the public key at `dify-plugin-public-key-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dify-plugin-public-key
  namespace: ai-search
data:
  plugin_public_key.pem: |
    -----BEGIN RSA PUBLIC KEY-----
    MIICC...
    -----END RSA PUBLIC KEY-----
```

---

## Step 6: Install via Dify UI

Now install the signed plugin through the Dify web interface:

### Install

1. **Navigate to Plugin Management:**
   - Log into your Dify instance
   - Click **Settings** → **Plugins** (or the plugin icon in the top right)
   - Click **Install Plugin** → **Local Package File**

### Upload Signed Package

1. **Navigate to Plugin Management:**
   - Log into your Dify instance
   - Click **Settings** → **Plugins**
   - Click **Install Plugin** → **Upload Package File**

2. **Upload the Signed Package:**
   - Click **Choose File**
   - Select `langf-plugin-pkg.signed.difypkg`
   - Click **Upload & Install**

3. **Verification:**
   - Dify will verify the signature using your configured public key
   - If verification fails, check your daemon configuration

---

## Step 7: Configure Langfuse Credentials

After installation, configure the plugin with your Langfuse credentials:

### Via Dify UI

1. **Navigate to Installed Plugins:**
   - Go to **Settings** → **Plugins**
   - Find **Langfuse** in the installed plugins list
   - Click **Authorization** 

2. **Enter Credentials:**
   - **Langfuse Public Key**: Your Langfuse API public key
   - **Langfuse Secret Key**: Your Langfuse API secret key
   - **Langfuse Host**: `https://langfuse.attraqt.dev`


## Step 8: Using the Plugin in Workflows

Once installed and configured, use the Langfuse tools in your Dify workflows:

### Available Tools

1. **Get Prompt Tool**
   - Retrieves specific prompts from Langfuse
   - Input: `name`, `label`, `version`, `variables`
   - Output: Prompt content with variable substitution

2. **Search Prompts Tool**
   - Searches for prompts in Langfuse
   - Input: Search criteria
   - Output: List of matching prompts

3. **Update Prompt Tool**
   - Creates new prompt versions in Langfuse
   - Input: `name`, `content`, `tags`, `labels`
   - Output: Updated prompt details
