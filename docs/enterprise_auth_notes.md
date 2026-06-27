# Enterprise Auth Notes

The repository implements JWT/RBAC auth with demo users and hashed API keys for local evaluation and CI workflows. It does not claim enterprise IAM or SSO.

A production team could add enterprise authentication using:

- Authlib with OIDC
- Keycloak
- Auth0
- Microsoft Entra ID
- Okta
- SAML behind an identity-aware proxy

Recommended future design:

1. Replace demo login with OIDC authorization code flow.
2. Map identity-provider groups to LLMShield roles.
3. Store users as externally managed identities.
4. Rotate refresh tokens.
5. Add session revocation and device inventory.
6. Enforce MFA at the identity provider.
7. Add organization/project-level permissions.
