async def on_shutdown(app):
    await app.users_client.session.close()
    await app.tasks_client.session.close()


def round_statistics(obj):
    if isinstance(obj, float):
        return round(obj, 3)
    if isinstance(obj, list):
        return [round_statistics(item) for item in obj]
    if isinstance(obj, dict):
        return {key: round_statistics(value) for key, value in obj.items()}
    return obj
