import java.util.ArrayList;
import java.util.List;

class Node {
    int id;
    boolean active;

    Node(int id) {
        this.id = id;
        this.active = true;
    }
}

public class RingElection {
    public static void main(String[] args) {
        int numberOfNodes = 5;
        List<Node> nodes = new ArrayList<>();

        // Inicializa os nós
        for (int i = 0; i < numberOfNodes; i++) {
            nodes.add(new Node(i));
        }

        // Desativa alguns nós para simular falhas
        nodes.get(1).active = false;
        nodes.get(3).active = false;

        int electedLeader = startElection(nodes);
        System.out.println("Líder eleito: Nó " + electedLeader);
    }

    public static int startElection(List<Node> nodes) {
        int n = nodes.size();
        int leaderId = -1;

        for (int i = 0; i < n; i++) {
            if (nodes.get(i).active) {
                int currentId = nodes.get(i).id;
                int nextId = (i + 1) % n;

                while (nextId != i) {
                    if (nodes.get(nextId).active && nodes.get(nextId).id > currentId) {
                        currentId = nodes.get(nextId).id;
                    }
                    nextId = (nextId + 1) % n;
                }

                if (currentId > leaderId) {
                    leaderId = currentId;
                }
            }
        }

        return leaderId;
    }
}
