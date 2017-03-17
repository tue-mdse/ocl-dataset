import org.eclipse.ocl.pivot.resource.ASResource;
import org.eclipse.ocl.pivot.utilities.ParserException;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class Main {

    private static Walker walker = new Walker();
    private static FileParser parser = new FileParser();

    public static void main(String[] args) {
        List<String> argsList = new LinkedList<>(Arrays.asList(args));
        boolean verbose = false;
        if (argsList.contains("-v")) {
            verbose = true;
            argsList.removeIf(a -> a.equals("-v"));
        }
        try {
            switch (args[0]) {
                case "operations":
                    operations(args[1]);
                    break;
                case "count":
                    System.out.print(countOclExpressions(args[1]));
                    break;
                case "save":
                    System.out.print(store(args[1], args[2], verbose));
                    break;
                case "walk":
                    walk(args[1]);
                    break;
                default:
                    System.out.print("unsupported");
            }
        } catch (Exception e) {
            e.printStackTrace(System.out);
        }
    }

    private static void operations(String filePath) throws ParserException {
        ASResource as = parser.toAs(filePath);
        walker.printOperations(as);
    }

    private static void walk(String filePath) throws ParserException {
        ASResource as = parser.toAs(filePath);
        walker.printTree(as);
    }

    private static int countOclExpressions(String filePath) throws ParserException {
        ASResource as = parser.toAs(filePath);
        return walker.countOclExpressions(as);
    }

    private static int store(String input, String output, boolean verbose) throws ParserException, IOException {
        ASResource as = parser.toAs(input);
        int count = walker.parseOclExpressions(as, verbose);
        Map<Object, Object> options = as.getDefaultSaveOptions();
        as.save(new FileWriter(output), options);
        return count;
    }
}
