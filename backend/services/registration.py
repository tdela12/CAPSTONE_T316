from fastapi import HTTPException, status

def lookup_registration(app, registration: str):
    """
    Looks up a car registration in the loaded dataset.
    """

    df = app.state.rego_data
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration data not loaded"
        )
    print(df.shape)
    
    filtered = df[df["Registration"] == registration]

    if filtered.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found"
        )

    return filtered.to_dict(orient="records")[0]
