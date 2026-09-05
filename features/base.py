from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureValue:
    """
    1つの特徴量について、先手・後手の値を保持する。

    black:
        先手側の特徴量
    white:
        後手側の特徴量
    """

    black: float
    white: float

    @property
    def difference(self) -> float:
        """
        先手 - 後手の差。
        """
        return self.black - self.white

    @property
    def mean(self) -> float:
        """
        先手・後手の平均値。

        両者の差が小さくても、両者とも高い状態を
        表現するために使用する。
        """
        return (self.black + self.white) / 2.0


class Feature(ABC):
    """
    40特徴量の共通インターフェース。
    """

    feature_id: str
    name: str
    category: str
    classification: str

    @abstractmethod
    def extract(self, board) -> FeatureValue:
        """
        現在局面から特徴量を抽出する。
        """
        raise NotImplementedError