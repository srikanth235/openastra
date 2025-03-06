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
            # Format the Hurl script to get request bodies
            format_process = subprocess.Popen(
                ["hurlfmt", "--out", "json", temp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            format_stdout, format_stderr = format_process.communicate()

            # Parse the formatted output if available
            formatted_data = None
            if format_stdout and format_process.returncode == 0:
                import json

                try:
                    formatted_data = json.loads(format_stdout)
                except json.JSONDecodeError:
                    pass

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

            print(f"Hurl script executed with exit code {process.returncode}")

            # Parse the time from the JSON output if available
            time_ms = 0
            hurl_result = None
            if stdout and process.returncode == 0:
                import json

                try:
                    hurl_result = json.loads(stdout)
                    time_ms = hurl_result.get("time", 0)

                    # Merge the formatted request data with the execution results
                    if (
                        formatted_data
                        and hurl_result
                        and "entries" in formatted_data
                        and "entries" in hurl_result
                    ):
                        # Ensure both lists have entries to merge
                        min_entries = min(
                            len(formatted_data["entries"]), len(hurl_result["entries"])
                        )

                        for i in range(min_entries):
                            # Replace entire request objects in the hurl_result with those from formatted_data
                            if (
                                "request" in formatted_data["entries"][i]
                                and "calls" in hurl_result["entries"][i]
                            ):
                                for call in hurl_result["entries"][i]["calls"]:
                                    call["request"] = formatted_data["entries"][i][
                                        "request"
                                    ]

                except json.JSONDecodeError:
                    pass
            print(f"Hurl result: {hurl_result}")
            return HurlExecuteResponse(
                success=process.returncode == 0,
                output=hurl_result,
                exit_code=process.returncode,
                time=time_ms,
            )
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute Hurl script: {str(e)}"
        )
