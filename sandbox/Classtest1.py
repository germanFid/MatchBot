CUP_TYPE_1 = 'Поильник'

class Bottle:
    def __init__(self, brand_name, volume, cup):
        self.brand_name = brand_name
        self.volume = volume
        self.cup = cup

        self.contains_water = 0
    
    def fill_with_water(self, volume_in_liters):
        how_much_is_filled = self.contains_water * self.volume
        how_much_is_left = self.volume - how_much_is_filled

        if volume_in_liters == 0:
            return

        if how_much_is_left == 0 or volume_in_liters > how_much_is_left:
            return -1

        final_filled = volume_in_liters + how_much_is_filled
        self.contains_water = final_filled / self.volume
    
    def how_much_is_filled(self):
        return self.volume * self.contains_water
    
kaplik = Bottle('кап-лик', 0.33, CUP_TYPE_1)

kaplik.fill_with_water(0.25)
print(kaplik.how_much_is_filled())

print(kaplik.fill_with_water(0.25))
