mod constants;
mod resources;
mod schema;
mod server;

use anyhow::Result;
use rmcp::{transport::stdio, ServiceExt};

use server::LarkinServer;

/// Ok so again, another note for myself.
/// 
/// ServiceExt is how `.serve()` is implemented. From the underlying code:
/// ```rust
/// pub trait ServiceExt<R: ServiceRole>: Service<R> + Sized {
///    fn into_dyn(self) -> Box<dyn DynService<R>> {
///        Box::new(self)
///    }
///    fn serve<T, E, A>(
///        self,
///        transport: T,
///    ) -> impl Future<Output = Result<RunningService<R, Self>, R::InitializeError>> + Send
///    where
///        T: IntoTransport<R, E, A>,
///        E: std::error::Error + Send + Sync + 'static,
///        Self: Sized,
///    {
///        Self::serve_with_ct(self, transport, Default::default())
///    }
/// ```
/// If you don't include `ServiceExt`, then you won't get .serve for free
/// 
/// Basically, what's happening is when you call .serve then Rust will check all the traits in scope
/// And see if there is one that implements it for your server.
/// So when we import ServiceExt, Rust will see that LarkinServer implements it and
/// add the .serve method to the server. More explicitly, Rust will see that LarkinServer implements
/// ServerHandler and so it knows ServiceExt can be applied.
/// 
/// Finally, the service.waiting().await is just saying keep the server alive until a disconnect.
#[tokio::main]
async fn main() -> Result<()> {
    let server = LarkinServer::new();
    let service = server.serve(stdio()).await?;
    service.waiting().await?;
    Ok(())
}
