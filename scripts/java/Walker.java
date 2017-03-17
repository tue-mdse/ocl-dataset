import org.eclipse.emf.common.util.EList;
import org.eclipse.emf.common.util.TreeIterator;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.ocl.pivot.*;
import org.eclipse.ocl.pivot.resource.ASResource;
import org.eclipse.ocl.pivot.utilities.OCL;
import org.eclipse.ocl.pivot.utilities.ParserException;
import org.eclipse.ocl.xtext.completeocl.CompleteOCLStandaloneSetup;

import java.util.Collection;
import java.util.LinkedList;

class Walker {
    Walker() {
        CompleteOCLStandaloneSetup.doSetup();
    }

    int countOclExpressions(ASResource as) {
        return countOclExpressions(as.getModel());
    }

    int parseOclExpressions(ASResource as, boolean verbose) throws ParserException {
        OCL ocl = OCL.newInstance(OCL.NO_PROJECTS, new ResourceSetImpl());
        Collection<ExpressionInOCL> expressions = new LinkedList<>();
        collectOclExpressions(as.getModel(), expressions);
        int errors = 0;
        for (ExpressionInOCL expression : expressions) {
            try {
                ocl.parseSpecification(expression);
            } catch (Exception e) {
                if (verbose) {
                    e.printStackTrace();
                }
                errors++;
            }
        }
        return expressions.size() - errors;
    }

    private void collectOclExpressions(EObject object, Collection<ExpressionInOCL> expressions) {
        if (object instanceof ExpressionInOCL) {
            expressions.add((ExpressionInOCL) object);
        }

        object.eContents().forEach(o -> this.collectOclExpressions(o, expressions));
    }

    private int countOclExpressions(EObject object) {
        if (object instanceof ExpressionInOCL) {
            return 1;
        }

        return object.eContents().stream().mapToInt(this::countOclExpressions).sum();
    }

    void printTree(ASResource as) {
        printTree(as.getContents(), 0);
    }

    private void printTree(EList<EObject> contents, int depth) {
        contents.forEach(object -> this.printTree(object, depth));
    }

    private void printTree(EObject object, int depth) {
        for (int i = 0; i < depth; i++) {
            System.out.print(" ");
        }
        System.out.println(object.getClass().getName());
        printTree(object.eContents(), depth + 1);
    }

    void printOperations(ASResource as) {
        TreeIterator<EObject> allContents = as.getAllContents();
        while (allContents.hasNext()) {
            EObject object = allContents.next();
            if (object instanceof OperationCallExp) {
                Operation referredOperation = ((OperationCallExp) object).getReferredOperation();
                if (referredOperation != null) {
                    String name = referredOperation.getName();
                    if (name != null) {
                        System.out.println(name);
                    }
                }
            }
        }
    }

}
