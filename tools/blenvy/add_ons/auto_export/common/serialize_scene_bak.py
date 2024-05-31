  #print("THIS IS A GEOMETRY NODE") 

        # storage for hashing
        links_hashes = []
        nodes_hashes = []
        modifier_inputs = dict(modifier_data)

        for node in node_group.nodes:
            #print("node", node, node.type, node.name, node.label)
            #print("node info", dir(node))

            input_hashes = []
            for input in node.inputs:
                #print(" input", input, "label", input.label, "name", input.name)
                input_hash = f"{getattr(input, 'default_value', None)}"
                input_hashes.append(input_hash)
                """if hasattr(input, "default_value"):
                    print("YOHO", dict(input), input.default_value)"""

            output_hashes = []
            # IF the node itself is a group input, its outputs are the inputs of the geometry node (yes, not easy)
            node_in_use = True
            for (index, output) in enumerate(node.outputs):
                # print(" output", output, "label", output.label, "name", output.name, "generated name", f"Socket_{index+1}")
                output_hash = f"{getattr(output, 'default_value', None)}"
                output_hashes.append(output_hash)
                """if hasattr(output, "default_value"):
                    print("YOHO", output.default_value)"""
                node_in_use = node_in_use and hasattr(output, "default_value")
            #print("NODE IN USE", node_in_use)

            node_fields_to_ignore = fields_to_ignore_generic + ['internal_links', 'inputs', 'outputs']

            node_hash = f"{generic_fields_hasher(node, node_fields_to_ignore)}_{str(input_hashes)}_{str(output_hashes)}"
            #print("node hash", node_hash)
            nodes_hashes.append(node_hash)
            #print(" ")

        for link in node_group.links:
            """print("LINK", link) #dir(link)
            print("FROM", link.from_node, link.from_socket)
            print("TO", link.to_node, link.to_socket)"""

            from_socket_default = link.from_socket.default_value if hasattr(link.from_socket, "default_value") else None
            to_socket_default = link.to_socket.default_value if hasattr(link.to_socket, "default_value") else None
            link_hash = f"{link.from_node.name}_{link.from_socket.name}_{from_socket_default}+{link.to_node.name}_{link.to_socket.name}_{to_socket_default}"

            """if hasattr(link.from_socket, "default_value"):
                print("[FROM SOCKET]", link.from_socket.default_value)
            if hasattr(link.to_socket, "default_value"):
                print("[TO SOCKET]", link.to_socket.default_value)"""

            links_hashes.append(link_hash)
            #print("link_hash", link_hash)

        return f"{str(modifier_inputs)}_{str(nodes_hashes)}_{str(links_hashes)}"