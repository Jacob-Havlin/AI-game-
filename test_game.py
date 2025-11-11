# test_game.py
import unittest
from unittest.mock import patch, MagicMock
import game  # This imports the game file we just created

class TestPlayerClass(unittest.TestCase):
    """
    Tests for the Player class and its core mechanics.
    """
    
    def setUp(self):
        """
        This method runs before each test.
        We create a new player for every test to ensure they are isolated.
        """
        self.player = game.Player("TestHero")
    
    def test_guardian_creation(self):
        self.player.setup_class("Guardian")
        self.assertEqual(self.player.char_class, "Guardian")
        self.assertEqual(self.player.stats['strength'], 15)
        self.assertEqual(self.player.max_hp, 120)
        self.assertEqual(self.player.hp, 120)
        # Check if the starter sword and potions are in inventory
        item_names = [item.name for item in self.player.inventory]
        self.assertIn("Soldier's Sword", item_names)
        self.assertIn("Health Potion", item_names)

    def test_mage_creation(self):
        self.player.setup_class("Mage")
        self.assertEqual(self.player.char_class, "Mage")
        self.assertEqual(self.player.stats['magic'], 18)
        self.assertEqual(self.player.max_hp, 80)
        self.assertEqual(self.player.mp, 80)
        item_names = [item.name for item in self.player.inventory]
        self.assertIn("Apprentice Staff", item_names)

    def test_shadow_creation(self):
        self.player.setup_class("Shadow")
        self.assertEqual(self.player.char_class, "Shadow")
        self.assertEqual(self.player.stats['agility'], 16)
        self.assertEqual(self.player.max_hp, 90)
        self.assertEqual(self.player.mp, 50)
        item_names = [item.name for item in self.player.inventory]
        self.assertIn("Twin Daggers", item_names)

    def test_take_damage(self):
        self.player.hp = 100
        # Mocking type_text to avoid printing during tests
        with patch('game.type_text'):
            self.player.take_damage(30)
        self.assertEqual(self.player.hp, 70)
    
    def test_take_fatal_damage(self):
        self.player.hp = 20
        with patch('game.type_text'):
            self.player.take_damage(50)
        self.assertEqual(self.player.hp, 0)
        self.assertFalse(self.player.is_alive())

    def test_is_alive(self):
        self.player.hp = 1
        self.assertTrue(self.player.is_alive())
        self.player.hp = 0
        self.assertFalse(self.player.is_alive())
        self.player.hp = -10
        self.assertFalse(self.player.is_alive())

    def test_use_health_potion(self):
        self.player.setup_class("Guardian") # Has 120 max HP
        self.player.hp = 50
        potion = game.Item("Health Potion", "Restores 25 HP.", "potion", ('heal', 25))
        self.player.inventory = [potion]
        
        # We patch 'print' because use_item prints to console
        with patch('builtins.print'):
            self.player.use_item(potion)
        
        self.assertEqual(self.player.hp, 75)
        self.assertNotIn(potion, self.player.inventory)

    def test_use_health_potion_at_full(self):
        self.player.setup_class("Guardian") # Has 120 max HP
        self.player.hp = 120
        potion = game.Item("Health Potion", "Restores 25 HP.", "potion", ('heal', 25))
        self.player.inventory = [potion]
        
        with patch('builtins.print'):
            self.player.use_item(potion)
        
        self.assertEqual(self.player.hp, 120)
        # Item should NOT be consumed if health is full
        self.assertIn(potion, self.player.inventory)

    def test_use_health_potion_overheal(self):
        self.player.setup_class("Guardian") # Has 120 max HP
        self.player.hp = 110
        potion = game.Item("Health Potion", "Restores 25 HP.", "potion", ('heal', 25))
        self.player.inventory = [potion]
        
        with patch('builtins.print'):
            self.player.use_item(potion)
        
        self.assertEqual(self.player.hp, 120) # Should cap at max HP
        self.assertNotIn(potion, self.player.inventory)


class TestCombatMechanics(unittest.TestCase):
    """
    Tests for combat functions, using 'patch' to mock dice rolls.
    """
    
    def setUp(self):
        self.player = game.Player("TestHero")
        self.player.setup_class("Mage") # str=6, agi=10, mag=18
        self.enemy = game.Enemy("Test Golem", 50, 10, 5, 0, "A test.")
    
    # We patch the 'random' module's functions
    @patch('game.random.randint')
    @patch('game.random.random')
    def test_player_attack_normal(self, mock_random, mock_randint):
        # Mock random.random() to ensure no critical hit (returns 0.9, > crit_chance)
        mock_random.return_value = 0.9
        # Mock random.randint() to return 2 for a predictable roll
        # Damage = str (6) + randint(-2, 5) -> 6 + 2 = 8
        mock_randint.return_value = 2
        
        with patch('game.type_text'):
            self.player.attack(self.enemy)
            
        self.assertEqual(self.enemy.hp, 42) # 50 - 8 = 42

    @patch('game.random.randint')
    @patch('game.random.random')
    def test_player_attack_critical(self, mock_random, mock_randint):
        # Mock random.random() to force a critical hit (returns 0.0, < crit_chance)
        mock_random.return_value = 0.0
        # Mock random.randint() to return 2
        # Base Damage = str (6) + 2 = 8
        # Crit Damage = int(8 * 1.8) = 14
        mock_randint.return_value = 2
        
        with patch('game.type_text'):
            self.player.attack(self.enemy)
            
        self.assertEqual(self.enemy.hp, 36) # 50 - 14 = 36

    @patch('game.random.randint')
    def test_player_special_move_mage(self, mock_randint):
        # Mock randint(8, 15) to return 10
        # Damage = magic (18) + 10 = 28
        mock_randint.return_value = 10
        
        with patch('game.type_text'):
            success = self.player.special_move(self.enemy)
        
        self.assertTrue(success)
        self.assertEqual(self.enemy.hp, 22) # 50 - 28 = 22
        self.assertEqual(self.player.mp, 65) # 80 - 15 = 65

    def test_player_special_move_no_mp(self):
        self.player.mp = 10 # Cost is 15
        
        with patch('game.type_text'):
            success = self.player.special_move(self.enemy)
        
        self.assertFalse(success) # Action should fail
        self.assertEqual(self.enemy.hp, 50) # No damage
        self.assertEqual(self.player.mp, 10) # No MP cost

    @patch('game.random.randint')
    @patch('game.random.random')
    def test_enemy_attack_and_player_defend(self, mock_random, mock_randint):
        # Mock random.random() to prevent dodge
        mock_random.return_value = 0.9
        # Mock randint(1, 6) to return 4
        # Enemy str = 10. Damage = 10 + 4 = 14
        mock_randint.return_value = 4
        
        # Player chooses to defend
        self.player.is_defending = True
        
        with patch('game.type_text'):
            self.enemy.attack(self.player)
            
        # Damage should be halved: 14 / 2 = 7
        self.assertEqual(self.player.hp, 73) # 80 - 7 = 73

# This allows running the tests from the command line
if __name__ == '__main__':
    unittest.main()