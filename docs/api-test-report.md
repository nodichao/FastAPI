# API Test Report

## 1. Objective

This document reports the manual and automated tests performed on the FastAPI backend.

The API exposes the following endpoints:

* `GET /health`
* `POST /chat`
* `POST /quiz`
* `POST /summarise`

The tests verify successful requests as well as validation errors.

---

## 2. Manual Tests with Swagger UI

### Test 1 — GET `/health`

**Request:**

```http
GET /health
```

**Expected result:**

* HTTP status: `200 OK`
* The response contains:

  * `status`
  * `version`
  * `timestamp`

**Observed result:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "..."
}
```

**Result:** PASS

---

### Test 2 — POST `/chat` — Valid Request

**Request body:**

```json
{
  "message": "Bonjour"
}
```

**Expected result:**

* HTTP status: `200 OK`
* The response contains an `answer` field.

**Observed result:**

```json
{
  "answer": "Welcome to the chat endpoint!"
}
```

**Result:** PASS

---

### Test 3 — POST `/chat` — Invalid Request

An invalid request was intentionally sent to verify Pydantic validation.

**Request body:**

```json
{
  "message": ""
}
```

The `message` field is invalid because the model requires at least one character.

**Expected result:**

* HTTP status: `422 Unprocessable Content`
* FastAPI returns validation details.

**Result:** PASS

---

### Test 4 — POST `/quiz` — Invalid Request

An invalid value was used for `nbQuestions`.

**Request body:**

```json
{
  "topic": "Python",
  "nbQuestions": 0
}
```

The value is invalid because the model defines:

```python
nbQuestions: int = Field(ge=1, le=20)
```

Therefore, `nbQuestions` must be between `1` and `20`.

**Expected result:**

* HTTP status: `422 Unprocessable Content`
* FastAPI reports a validation error.

**Result:** PASS

---

## 3. Automated Tests

Automated tests were implemented using `pytest` and FastAPI's `TestClient`.

The tests cover:

* `GET /health`
* `POST /chat`

The tests can be executed with:

```bash
python -m pytest
```

### Test result

```text
collected 2 items

tests\test_api.py .. [100%]

2 passed
```

### Automated test summary

| Endpoint  | Test          | Expected | Result |
| --------- | ------------- | -------- | ------ |
| `/health` | Valid request | `200 OK` | PASS   |
| `/chat`   | Valid request | `200 OK` | PASS   |

---

## 4. Validation Tests

Pydantic validation was also tested through Swagger UI.

| Endpoint | Input             | Expected result | Result |
| -------- | ----------------- | --------------- | ------ |
| `/chat`  | Empty message     | `422`           | PASS   |
| `/quiz`  | `nbQuestions = 0` | `422`           | PASS   |

These tests confirm that invalid request data is rejected before the endpoint logic is executed.

---

## 5. Conclusion

The FastAPI API was tested manually through Swagger UI and automatically using `pytest`.

The tests confirmed that:

* Valid requests are accepted.
* Invalid request bodies are rejected with HTTP `422`.
* Pydantic constraints are applied correctly.
* The `/health` and `/chat` endpoints behave as expected.
* Automated tests can be executed without manually starting the FastAPI development server.
