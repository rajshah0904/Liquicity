use actix_web::{web, App, HttpServer, HttpResponse, Responder};
use actix_cors::Cors;
use actix_session::{CookieSession, SessionMiddleware};
use sqlx::PgPool;
use dotenv::dotenv;
use std::env;
use security::SecurityService;

mod security;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();
    env_logger::init();

    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPool::connect(&database_url).await.unwrap();

    let security_service = web::Data::new(SecurityService::new(pool.clone()));

    HttpServer::new(move || {
        App::new()
            .wrap(
                Cors::default()
                    .allow_any_origin()
                    .allow_any_method()
                    .allow_any_header()
                    .max_age(3600)
            )
            .wrap(
                SessionMiddleware::builder(CookieSession::signed(&[0; 32]).unwrap())
                    .cookie_secure(true)
                    .cookie_http_only(true)
                    .build()
            )
            .app_data(security_service.clone())
            .service(
                web::scope("/api/security")
                    .route("/totp/generate", web::post().to(totp_generate))
                    .route("/totp/verify", web::post().to(totp_verify))
                    .route("/kyc/initiate", web::post().to(kyc_initiate))
                    .route("/kyc/check", web::get().to(kyc_check))
            )
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}

async fn totp_generate(
    pool: web::Data<PgPool>,
    req: web::Json<security::TotpRequest>,
) -> impl Responder {
    let service = SecurityService::new(pool.get_ref().clone());
    service.generate_totp_secret(&req.user_id).await
}

async fn totp_verify(
    pool: web::Data<PgPool>,
    req: web::Json<security::TotpRequest>,
) -> impl Responder {
    let service = SecurityService::new(pool.get_ref().clone());
    service.verify_totp(req).await
}

async fn kyc_initiate(
    pool: web::Data<PgPool>,
    req: web::Json<security::KycRequest>,
) -> impl Responder {
    let service = SecurityService::new(pool.get_ref().clone());
    service.initiate_kyc(req).await
}

async fn kyc_check(
    pool: web::Data<PgPool>,
    user_id: web::Path<String>,
) -> impl Responder {
    let service = SecurityService::new(pool.get_ref().clone());
    service.check_kyc_status(&user_id).await
} 