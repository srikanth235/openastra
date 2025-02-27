import os
import subprocess
import tempfile

from fastapi import APIRouter, HTTPException

from app.models.execute import HurlExecuteRequest, HurlExecuteResponse

router = APIRouter()


@router.post("/hurl", response_model=HurlExecuteResponse)
async def execute_hurl(
    request: HurlExecuteRequest,
) -> HurlExecuteResponse:
    """
    Execute a Hurl script and return the results
    """
    try:
        # Create a temporary file for the Hurl script
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".hurl", delete=False
        ) as temp:
            temp.write(request.script)
            temp_path = temp.name

        try:
            # Execute Hurl with the script using the --json flag
            process = subprocess.Popen(
                ["hurl", "--json", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate()

            # Combine stdout and stderr for the output
            output = []
            if stdout:
                output.extend(stdout.splitlines())
            if stderr:
                output.extend(stderr.splitlines())

            return HurlExecuteResponse(
                success=process.returncode == 0,
                output=output,
                exit_code=process.returncode,
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute Hurl script: {str(e)}"
        )
