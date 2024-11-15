from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from game.models import Game
from game.serializers import GameSerializer
from users.models import User
from rest_framework.permissions import IsAuthenticated

# View for starting a game
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_game(request):
    user = request.user
    opponent_id = request.data.get('opponent_id')

    try:
        opponent = User.objects.get(id=opponent_id)
    except User.DoesNotExist:
        return Response({'error': 'Opponent not found'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new game (both white and black players)
    game = Game.objects.create(white_player=user, black_player=opponent, result='Pending')

    return Response({'game_id': game.id, 'white_player': game.white_player.username, 'black_player': game.black_player.username}, status=status.HTTP_201_CREATED)

# Get a list of all users (excluding the logged-in user)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_opponents(request):
    user = request.user
    opponents = User.objects.exclude(id=user.id)  # Exclude the logged-in user from the list
    opponent_list = [{'id': opponent.id, 'username': opponent.username} for opponent in opponents]
    return Response(opponent_list, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_score(request, game_id):
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({'error': 'Game not found'}, status=status.HTTP_404_NOT_FOUND)

    result = request.data.get('result')  # The result could be "White", "Black", or "Draw"
    if result not in ['White', 'Black', 'Draw']:
        return Response({'error': 'Invalid result'}, status=status.HTTP_400_BAD_REQUEST)

    # Update game result
    game.result = result
    game.save()

    # Update player scores
    if result == 'White':
        game.white_player.score += 1
        game.white_player.save()
    elif result == 'Black':
        game.black_player.score += 1
        game.black_player.save()

    return Response({'msg': 'Game result and scores updated'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_history(request):
    user = request.user  # Get the currently logged-in user

    # Get all games where the user is either the white or black player
    games = Game.objects.filter(white_player=user) | Game.objects.filter(black_player=user)
    game_serializer = GameSerializer(games, many=True)

    return Response(game_serializer.data, status=status.HTTP_200_OK)