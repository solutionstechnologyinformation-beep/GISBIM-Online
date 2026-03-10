#[macro_use] extern crate rocket;

use std::env;
use rocket::fs::{FileServer, relative};

#[launch]
fn rocket() -> _ {
    let port: u16 = env::var("PORT")
        .unwrap_or_else(|_| "8000".to_string())
        .parse()
        .unwrap_or(8000);

    let config = rocket::Config {
        port,
        address: std::net::IpAddr::V4(std::net::Ipv4Addr::new(0, 0, 0, 0)),
        ..rocket::Config::default()
    };

    rocket::build()
        .configure(config)
        .mount("/", FileServer::from(relative!("static")))
}