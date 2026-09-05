import cshogi

from features.exchange import ExchangeFeature


def test_exchange_no_change():
    """局面に変化がなければ交換量は0になる。"""

    before = cshogi.Board()
    after = cshogi.Board()

    feature = ExchangeFeature()

    metrics = feature.calculate_metrics(
        before,
        after,
    )

    assert metrics.exchange_count == 0
    assert metrics.exchanged_value == 0
    assert metrics.major_exchange_value == 0
    assert metrics.minor_exchange_value == 0
    assert metrics.board_to_hand_value == 0
    assert metrics.composition_change == 0


def create_pawn_capture_position():
    """
    実際の合法手順で歩の取りを発生させる。

    7g7f
    3c3d
    2g2f
    8c8d
    2f2e
    3d3e
    2e2d
    8d8e
    2d2c+

    最後の2d2c+で黒の歩が白の歩を取る。
    """

    board = cshogi.Board()

    moves = [
        "7g7f",
        "3c3d",
        "2g2f",
        "8c8d",
        "2f2e",
        "3d3e",
        "2e2d",
        "8d8e",
        "2d2c+",
    ]

    for move in moves:
        board.push_usi(move)

    return board


def test_exchange_after_pawn_capture():
    """歩を取った場合、交換対象の駒が検出される。"""

    before = cshogi.Board()
    after = create_pawn_capture_position()

    feature = ExchangeFeature()

    metrics = feature.calculate_metrics(
        before,
        after,
    )

    assert metrics.exchange_count > 0
    assert metrics.exchanged_value > 0
    assert metrics.minor_exchange_value > 0


def test_exchange_feature_value_changes():
    """駒取りによってF03の値が変化する。"""

    before = cshogi.Board()
    after = create_pawn_capture_position()

    feature = ExchangeFeature()

    before_value = feature.extract(before)

    after_value = feature.extract_transition(
        before,
        after,
    )

    assert after_value.black > before_value.black
    assert after_value.white > before_value.white
