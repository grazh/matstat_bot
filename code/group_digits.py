def find_sequence(a, index):
	i = index
	while i < a.__len__()-1 and abs(a[i+1])-abs(a[i]) == 1:
		i += 1
	return i

def group_digits(array_1):
	index = 0
	j = 0
	new_array = []
	while index < len(array_1):
		if index + 1 < len(array_1) and array_1[index + 1] - array_1[index] == 1:
			new_array.append(str(array_1[index]))
			end = find_sequence(array_1, index)
			new_array[j] += '-'
			new_array[j] += str(array_1[end])
			j += 1
			index = end+1
		else:
			new_array.append(str(array_1[index]))
			j += 1
			index += 1
	return new_array
