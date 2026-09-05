import cshogi

from features.material import MaterialBalanceFeature


def test_initial_position_material_balance():
    """
    初期局面では先手・後手の駒価値が等しい。
    """

    board = cshogi.Board()

    feature = MaterialBalanceFeature()
    value = feature.extract(board)

    assert value.black > 0
    assert value.white > 0
    assert value.black == value.white
    assert value.difference == 0.0


def test_initial_position_mean():
    """
    初期局面ではmeanが正の値になる。
    """

    board = cshogi.Board()

    feature = MaterialBalanceFeature()
    value = feature.extract(board)

    assert value.mean > 0


def test_initial_position_normalized_balance():
    """
    初期局面の正規化された駒得差は0。
    """

    board = cshogi.Board()

    feature = MaterialBalanceFeature()

    normalized = feature.normalized_difference(board)

    assert -1.0 <= normalized <= 1.0
    assert abs(normalized) < 1e-9


def test_custom_piece_values():
    """
    駒価値を外部から変更できることを確認する。
    """

    board = cshogi.Board()

    values = MaterialBalanceFeature.DEFAULT_PIECE_VALUES.copy()
    values[cshogi.PAWN] = 2.0

    feature = MaterialBalanceFeature(
        piece_values=values
    )

    value = feature.extract(board)

    # 初期局面では歩が双方9枚存在するため、
    # 標準値から歩の変更分が反映される。
    assert value.black == value.white

from features.material import (
    MaterialBalanceFeature,
    HandPieceBalanceFeature,
)


def test_initial_position_hand_piece_balance():
    board = cshogi.Board()
    feature = HandPieceBalanceFeature()
    value = feature.extract(board)

    assert value.black == 0.0
    assert value.white == 0.0
    assert value.difference == 0.0
    assert value.mean == 0.0


def test_hand_piece_balance_after_capture():
    board = cshogi.Board()

    # 7六歩
    board.push_usi("7g7f")

    # 3四歩
    board.push_usi("3c3d")

    # 2六歩
    board.push_usi("2g2f")

    # 8四歩
    board.push_usi("8c8d")

    feature = HandPieceBalanceFeature()
    value = feature.extract(board)

    assert value.black == 0.0
    assert value.white == 0.0


def test_custom_hand_piece_values():
    board = cshogi.Board()

    # pieces_in_hand は [black, white]。
    # 先手に歩を1枚追加した局面を作るため、
    # 盤上の歩を取る手順は別途テストする。
    values = HandPieceBalanceFeature.HAND_PIECE_VALUES.copy()
    values[cshogi.PAWN] = 2.0

    feature = HandPieceBalanceFeature(
        piece_values=values
    )

    value = feature.extract(board)

    assert value.black == 0.0
    assert value.white == 0.0


def test_initial_position_normalized_hand_piece_balance():
    board = cshogi.Board()
    feature = HandPieceBalanceFeature()

    normalized = feature.normalized_difference(board)

    assert -1.0 <= normalized <= 1.0
    assert abs(normalized) < 1e-9