use anyhow::Result;
use rmcp::{transport::stdio, ServiceExt};

use larkin_mcp::LarkinServer;

#[tokio::main]
async fn main() -> Result<()> {
    let server = LarkinServer::new();
    let service = server.serve(stdio()).await?;
    service.waiting().await?;
    Ok(())
}
