"""Testing of only DocumentBaseModel from user.py. UserDoc and
UserDocUpdate have been indirectly tested in test_user_controller.py"""

from datetime import datetime

from kytos.core.user import DocumentBaseModel


def test_document_base_model_dict():
    """Test DocumentBaseModel.dict()"""
    _id = "random_id"
    utc_now = datetime.utcnow()
    payload = {"_id": _id, "inserted_at": utc_now, "updated_at": utc_now}
    model = DocumentBaseModel(**payload)
    assert model.dict(exclude_none=True) == {**payload, **{"id": _id}}
    assert "_id" not in model.dict(exclude={"_id"})
