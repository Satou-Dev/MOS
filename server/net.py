SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80

def read_varint(bytes_set):
    value = 0
    position = 0
    pos_byte = 0
    while True:
        current_byte = bytes_set[pos_byte]
        value |= (current_byte & SEGMENT_BITS) << position
        if (current_byte & CONTINUE_BIT) == 0:
            break

        position += 7
        pos_byte += 1

        if position >= 32:
            raise RuntimeError("VarInt is too big")

    return value

def write_varint(value):
    bytes_set = []
    while True:
        byte = value & SEGMENT_BITS
        value >>= 7
        if value:
            bytes_set.append(byte | CONTINUE_BIT)
        else:
            bytes_set.append(byte)
            break
    return bytes(bytes_set)

def encode_position(x, y, z):
    """
    Возвращает байтовое представление позиции ввиде строки
    :param int x: координата X
    :param int y: координата Y
    :param int z: координата Z
    :return: байтовое представление позиции
    """

    def twos_complement(num, bits):
        if num < 0:
            num = (1 << bits) + num
        return bin(num)[2:].zfill(bits)

    x_binary = twos_complement(x, 26)
    y_binary = twos_complement(y, 12)
    z_binary = twos_complement(z, 26)

    encoded_position = x_binary + z_binary + y_binary

    return encoded_position

def decode_position(encoded_data_str):
    """
    Возвращает координаты X, Y, Z
    :param str encoded_position: байтовое представление позиции
    :return: координаты X, Y, Z
    """
    negate_x, negate_y, negate_z = encoded_data_str[:26][0], encoded_data_str[26:52][0], encoded_data_str[52:][0]
    encoded_x, encoded_y, encoded_z = (int(encoded_data_str[1:26], 2),
                                       int(encoded_data_str[27:52], 2),
                                       int(encoded_data_str[53:], 2))
    data_x = [encoded_x, negate_x]
    data_y = [encoded_y, negate_y]
    data_z = [encoded_z, negate_z]

    return check_bin_number(data_x), check_bin_number(data_y), check_bin_number(data_z)

def count_bits(value):
    """
    Возвращает количество бит
    :param int value: байтовое представление числа ввиде целочисленного значения
    :return: кол-во бит
    """
    binary_representation = bin(value)[2:]
    num_bits = len(binary_representation)
    return num_bits

def check_bin_number(value_list):
    """
    Возвращает число из строки
    :param list value_list: битовое представление числа ввиде массива [биты, знак]
    :return: число (положительное или отрицательное)
    """
    value, negate = value_list
    bits_len = count_bits(value)
    if negate == "1":
        mask = (1 << bits_len + 1) - 1
        return -((value ^ mask) + 1)
    return value