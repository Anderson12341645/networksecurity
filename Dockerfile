name: Deployment Workflow

on:
  push:
    branches:
      - main
    paths-ignore:
      - 'README.md'

jobs:
  # ... [other jobs remain unchanged] ...

  continuous-deployment:
    name: Deploy to EC2
    needs: build-and-push-ecr-image
    runs-on: self-hosted
    steps:
      # ... [previous steps unchanged] ...

      - name: Generate self-signed certificates
        run: |
          mkdir -p ${{ github.workspace }}/certs
          openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ${{ github.workspace }}/certs/private.key \
            -out ${{ github.workspace }}/certs/certificate.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

      - name: Set image reference
        id: set-image-ref
        run: |
          IMAGE_REF="${{ steps.login-ecr-deploy.outputs.registry }}/${{ secrets.ECR_REPOSITORY_NAME }}:latest"
          # Only remove control characters (not slashes or other valid URL chars)
          CLEAN_IMAGE_REF=$(echo "$IMAGE_REF" | tr -d '[:cntrl:]')
          echo "CLEAN_IMAGE_REF=$CLEAN_IMAGE_REF" >> $GITHUB_ENV
          echo "Sanitized image ref length: ${#CLEAN_IMAGE_REF}"

      - name: Debug image reference
        run: |
          echo "Sanitized image reference: ${CLEAN_IMAGE_REF}"
          echo "Registry: ${{ steps.login-ecr-deploy.outputs.registry }}"
          echo "Repository: ${{ secrets.ECR_REPOSITORY_NAME }}"

      - name: Pull latest image
        run: |
          docker pull "$CLEAN_IMAGE_REF"

      # ... [stop container step unchanged] ...

      - name: Run new container
        run: |
          docker run -d \
            -p 8000:8000 \
            --ipc=host \
            --name=security \
            -v ${{ github.workspace }}/certs:/app/certs \
            -e DAGSHUB_TOKEN="${{ secrets.DAGSHUB_TOKEN }}" \
            -e AWS_ACCESS_KEY_ID="${{ secrets.AWS_ACCESS_KEY_ID }}" \
            -e AWS_SECRET_ACCESS_KEY="${{ secrets.AWS_SECRET_ACCESS_KEY }}" \
            -e "MONGODB_URL_KEY=${{ secrets.MONGODB_URL_KEY }}" \
            -e BIND=0.0.0.0:8000 \
            -e SSL_CERT_PATH=/app/certs/certificate.crt \
            -e SSL_KEY_PATH=/app/certs/private.key \
            "$CLEAN_IMAGE_REF"

      # ... [remaining steps unchanged] ...