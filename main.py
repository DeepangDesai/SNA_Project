import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import networkx.algorithms.community as nx_comm
from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities
from twitter import scrape
from count_utils import *
from colors_util import *

st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Recent Hashtag posts visualization')

name = st.text_input("Enter Hashtag", "#")
max_counter = 3
clicked = st.button('Plot Graph')
out_nodes = st.select_slider(
    'Select the number of outgoing edges from first layer',
    options=['3', '4', '5', '6', '7', '8'])
max_counter = int(out_nodes)
limit = st.slider('Select the minimum frequency cap', 0, 100, 0)
flimit = int(limit)

G = nx.MultiDiGraph()

counter = 0
d = {}
f = {}
fre = {}
done = [name]

if clicked:

    d[name] = scrape(name, 100)
    f[name] = frequency(d[name])
    fre[name] = 0

    G.add_node(name)
    for i in range(len(f[name])):
        s = 0
        if counter == 8:
            break
        cur = "#" + list(f[name].items())[i][0]

        for j in done:
            if similar(cur, j) > 0.8:
                s = 1
        if s == 1:
            continue
        else:
            d[cur] = scrape(cur, 100)
            done.append(cur)
            f[cur] = frequency(d[cur])
            counter = counter + 1
            G.add_node(cur)
            fre[cur] = f[name][i]
            G.add_edge(name, cur, weight=f[name][i])

    for i in range(7):
        counter = 0
        cur = done[i + 1]

        for j in range(len(f[cur])):
            sim = 0
            if counter == max_counter:
                break
            if similar(cur, "#" + list(f[cur].items())[j][0]) >= 0.8:
                continue
            counter = counter + 1
            for k in done:
                if similar("#" + list(f[cur].items())[j][0], k) >= 0.8:
                    sim = 1
                    G.add_edge(cur, k, weight=f[cur][j])
                    fre[k] = fre[k] + f[cur][j]
            if sim == 1:
                continue
            if "#" + list(f[cur].items())[j][0] in done:
                fre["#" + list(f[cur].items())[j][0]] = fre["#" + list(f[cur].items())[j][0]] + f[cur][j]
                G.add_edge(cur, "#" + list(f[cur].items())[j][0], weight=f[cur][j])
            else:
                G.add_node("#" + list(f[cur].items())[j][0])
                done.append("#" + list(f[cur].items())[j][0])
                fre["#" + list(f[cur].items())[j][0]] = f[cur][j]
                G.add_edge(cur, "#" + list(f[cur].items())[j][0], weight=f[cur][j])

    weights = list(zip(*nx.get_edge_attributes(G, 'weight').items()))
    w = list(weights[1])

    xmin = min(w)
    xmax = max(w)
    for i, x in enumerate(w):
        w[i] = ((x - xmin) / (xmax - xmin)) * 3

    communities = greedy_modularity_communities(G, weight=weights[1], resolution=1)

    in_degree = []
    for i in done:
        in_degree.append(G.in_degree(i) * 500)

    for c, v_c in enumerate(communities):
        for v in v_c:
            G.nodes[v]['community'] = c + 1
    node_color = [get_color(G.nodes[v]['community']) for v in G.nodes]
    node_color[0] = (1, 0, 0)

    sample = [done[0]]
    shells = [sample, done[1:9], done[9:]]
    pos = nx.shell_layout(G, shells)
    for i in pos:
        pos[i] = pos[i] * 5
    amb = len(G.nodes())
    coun = -1
    for i in done:
        coun = coun + 1
        if fre[i] < flimit:
            G.remove_node(i)
            node_color.pop(coun)
            in_degree.pop(coun)
            w.pop(coun)
            coun = coun - 1
    fig = plt.figure()
    nx.draw(G, pos, edge_color='white', width=w, node_size=in_degree, node_color=node_color, with_labels=True,
            font_color='cyan', alpha=0.9)
    fig.set_facecolor("black")
    st.pyplot()
    ambiguity = (amb - 9) / (8 * max_counter)
    st.write("Ambiguity of group of hashtags is", ambiguity)
