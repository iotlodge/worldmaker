"""Code repository endpoints for microservice source code."""
from __future__ import annotations

try:
    from fastapi import APIRouter, Depends, Path, HTTPException
    from fastapi.responses import PlainTextResponse
    from typing import Any

    from worldmaker.api.deps import get_memory_store, get_code_repo_manager
    from worldmaker.db.memory import InMemoryStore
    from worldmaker.codegen import CodeRepoManager

    router = APIRouter()

    @router.get("/microservices/{ms_id}/code")
    async def get_code_manifest(
        ms_id: str = Path(..., description="Microservice ID"),
        store: InMemoryStore = Depends(get_memory_store),
        code_mgr: CodeRepoManager = Depends(get_code_repo_manager),
    ) -> dict[str, Any]:
        """Get file manifest for a microservice's code repository."""
        ms = store.get("microservice", ms_id)
        if not ms:
            raise HTTPException(404, f"Microservice {ms_id} not found")

        ms_name = ms["name"]
        manifest = code_mgr.get_manifest(ms_name)
        if not manifest:
            raise HTTPException(404, f"No code repository for {ms_name}")

        manifest["microservice_id"] = ms_id
        manifest["language"] = ms.get("language", "unknown")
        manifest["framework"] = ms.get("framework", "")
        return manifest

    @router.get("/microservices/{ms_id}/code/{filename}")
    async def get_code_file(
        ms_id: str = Path(..., description="Microservice ID"),
        filename: str = Path(..., description="File name"),
        store: InMemoryStore = Depends(get_memory_store),
        code_mgr: CodeRepoManager = Depends(get_code_repo_manager),
    ) -> dict[str, Any]:
        """Get content of a specific file from a microservice repo."""
        ms = store.get("microservice", ms_id)
        if not ms:
            raise HTTPException(404, f"Microservice {ms_id} not found")

        content = code_mgr.get_file_content(ms["name"], filename)
        if content is None:
            raise HTTPException(404, f"File {filename} not found in {ms['name']}")

        return {
            "microservice_id": ms_id,
            "filename": filename,
            "content": content,
            "size": len(content),
        }

    @router.post("/microservices/{ms_id}/code/scaffold")
    async def scaffold_code(
        ms_id: str = Path(..., description="Microservice ID"),
        store: InMemoryStore = Depends(get_memory_store),
        code_mgr: CodeRepoManager = Depends(get_code_repo_manager),
    ) -> dict[str, Any]:
        """Manually trigger code generation for a microservice."""
        ms = store.get("microservice", ms_id)
        if not ms:
            raise HTTPException(404, f"Microservice {ms_id} not found")

        manifest = code_mgr.scaffold(ms)
        return {"status": "scaffolded", "manifest": manifest}

    @router.delete("/microservices/{ms_id}/code")
    async def delete_code(
        ms_id: str = Path(..., description="Microservice ID"),
        store: InMemoryStore = Depends(get_memory_store),
        code_mgr: CodeRepoManager = Depends(get_code_repo_manager),
    ) -> dict[str, Any]:
        """Remove code repository for a microservice."""
        ms = store.get("microservice", ms_id)
        if not ms:
            raise HTTPException(404, f"Microservice {ms_id} not found")

        deleted = code_mgr.delete_repo(ms["name"])
        return {"deleted": deleted, "microservice_id": ms_id}

except ImportError:
    router = None
