from fastapi.responses import JSONResponse


def register_health_routes(app, get_db_connection):
    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "project": "ArtToSlipAway"
        }


    @app.get("/health/db")
    async def health_db():
        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("SELECT 1;")
            cursor.fetchone()

            return {
                "status": "ok",
            }

        except Exception:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "detail": "Database unavailable"},
            )

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()
