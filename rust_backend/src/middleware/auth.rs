use actix_web::{dev::ServiceRequest, Error, HttpMessage, HttpRequest};
use futures::future::{ready, Ready};
use jsonwebtoken::{decode, Validation};
use serde::{Deserialize, Serialize};
use std::env;

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,      // Subject (user id)
    pub iss: String,      // Issuer
    pub aud: String,      // Audience
    pub exp: usize,      // Expiration time
    pub iat: usize,      // Issued at
    pub scope: String,   // OAuth scope
}

pub struct AuthMiddleware;

impl<S, B> actix_web::middleware::Middleware<S> for AuthMiddleware
where
    S: 'static,
    B: 'static,
{
    type Response = Ready<Result<ServiceRequest, Error>>;

    fn check(&self, req: &mut ServiceRequest) -> Self::Response {
        let auth_header = req
            .headers()
            .get("Authorization")
            .and_then(|h| h.to_str().ok())
            .and_then(|h| h.strip_prefix("Bearer "));

        match auth_header {
            Some(token) => {
                let validation = Validation {
                    validate_exp: true,
                    validate_nbf: true,
                    validate_iat: true,
                    ..Validation::default()
                };

                let auth0_domain = env::var("AUTH0_DOMAIN").expect("AUTH0_DOMAIN must be set");
                let auth0_audience = env::var("AUTH0_AUDIENCE").expect("AUTH0_AUDIENCE must be set");

                match decode::<Claims>(
                    token,
                    &DecodingKey::from_jwk_set_url(&format!("https://{}/.well-known/jwks.json", auth0_domain))
                        .expect("Failed to create decoding key"),
                    &validation,
                ) {
                    Ok(token_data) => {
                        if token_data.claims.aud != auth0_audience {
                            return ready(Err(Error::from("Invalid audience")));
                        }

                        req.extensions_mut().insert(token_data.claims);
                        ready(Ok(req.take_request()))
                    }
                    Err(_) => ready(Err(Error::from("Invalid token"))),
                }
            }
            None => ready(Err(Error::from("Missing token"))),
        }
    }
}
