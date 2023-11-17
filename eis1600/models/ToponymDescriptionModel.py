from eis1600.models.Model import Model
from eis1600.helper.Singleton import singleton


@singleton
class ToponymDescriptionModel(Model):

    def __init__(self) -> None:
        super().__init__('EIS1600_Pretrained_Models/camelbert-ca-toponyms-description/')


