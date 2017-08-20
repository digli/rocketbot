player = blue_player if self.team == 'blue' else orange_player
opponent = blue_player if self.team == 'orange' else orange_player

ball = {
    'position': {
        'x': input[0][7],
        'z': input[0][2],
        'y': input[0][6]
    },
    'velocity': {
        'x': input[0][31],
        'y': input[0][32],
        'z': input[0][33]
    }
}

blue_player = {
    'boost': input[0][0], # 0-100
    'position': {
        'z': input[0][1],       
        'y': input[0][4],
        'x': input[0][5],
    },
    'velocity': {
        'x': input[0][28],
        'y': input[0][29],
        'z': input[0][30]
    },
    'rotation': [
        # phi = atan2(z, x)

        # rot1 
        # sin(phi)
        input[0][8], # 1 when front of car pointing towards positive x, 0 when front of car facing z direction, -1 when facing -x direction.  Angles in between filled in.

        # rot2 
        # car.up == world.up ? cos(phi) : -cos(phi)
        input[0][9], # Same as Rot4 but when upside down 1 and -1 switched.

        # rot3
        input[0][10], # Bottom of wheels facing ground/ceiling = 0.  Wheels facing -x = 1, wheels facing +x = -1
        
        # rot4 
        # cos(phi)
        input[0][11], # 1 when front of car facing positive z, -1 when facing negative z, 0 when facing + or - x.
        
        # rot5
        # car.up == world.up ? sin(phi) : -sin(phi)
        input[0][12], # Same as Rot1 except when upside down 1 and -1 switched.
        
        # rot6
        input[0][13], # Wheels facing -z = 1, wheels facing +z = -1, wheels on ground / ceiling = 0
        
        # rot7
        input[0][14], # Car nose facing up = 1, car nose facing down = -1, car on ground/ceiling = 0
        
        # rot8
        input[0][15], # Wheels +x and nose +z = -1, wheels +x and nose -z = 1, wheels -x and nose +z = 1, wheels -x and nose -z = -1
        
        # rot9
        input[0][16], # Wheels on ground = 1, wheels facing ceiling = -1, wheels on wall = 0
    ]
}

# ... repeat for orange


output = [
    'stickX',
    'styckY',
    'acceleration',
    'retardation',
    'jump',
    'boost',
    'powerslide'
]


