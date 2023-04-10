from anytree import Node , RenderTree, findall

root = Node("root", text='')
node_dict = {}

pairs = []
with open('./titles/new_title.txt', 'r') as file:
    part = file.read().split('\n')

for element in part:
    if len(element) > 3:
        title_level = element[2]
        title_text = element[5:]
        title_text = title_text.replace('', '')
        pairs.append((title_level, title_text))


for title_level, title_text in pairs:
    if title_level == '1' and title_text[1].isdigit():  # 一级标题
        node = Node(title_text, parent=root)

for title_level, title_text in pairs:
    if title_level == '2':
        parent_title = title_text.split('.')[0]
        if parent_title.isdigit():
            parent_name = '第' + parent_title + '章'
            parent_node = findall(root, filter_=lambda node: node.name == parent_name)[0]
            child_node = Node(title_text, parent=parent_node)

for title_level, title_text in pairs:
    if title_level == '3':
        title_parts = title_text.split('.', 2)
        # print(title_parts)
        if len(title_parts) == 3:
            title_new = title_parts[0] + '.' + title_parts[1]
            parent_node = findall(root, filter_=lambda node: node.name.startswith(title_new))[0]
            child_node = Node(title_text, parent=parent_node)



for pre, fill, node in RenderTree(root):
    print("%s%s" % (pre, node.name))

with open('./titles/tree.txt', 'w') as file:
    for pre, fill, node in RenderTree(root):
        file.write("%s%s\n" % (pre, node.name))
