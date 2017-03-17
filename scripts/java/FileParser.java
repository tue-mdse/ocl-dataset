import org.eclipse.emf.common.util.URI;
import org.eclipse.emf.ecore.resource.Resource;
import org.eclipse.emf.ecore.resource.impl.ResourceSetImpl;
import org.eclipse.ocl.pivot.resource.ASResource;
import org.eclipse.ocl.pivot.utilities.OCL;
import org.eclipse.ocl.pivot.utilities.ParserException;
import org.eclipse.ocl.xtext.completeocl.CompleteOCLStandaloneSetup;

class FileParser {

    FileParser() {
        CompleteOCLStandaloneSetup.doSetup();
    }

    ASResource toAs(String filePath) throws ParserException {
        URI uri = URI.createFileURI(filePath);
        String e = uri.fileExtension();
        switch (e) {
            case "ecore":
                return ecoreToAs(uri);
            case "ocl":
                return oclToAs(uri);
            case "oclas":
                return getAs(uri);
            default:
                throw new RuntimeException("Unsupported Extension: " + e);
        }
    }

    private ASResource getAs(URI uri) {
        ResourceSetImpl rs = new ResourceSetImpl();
        return (ASResource) rs.getResource(uri, true);
    }

    private ASResource oclToAs(URI uri) {
        OCL ocl = OCL.newInstance(OCL.NO_PROJECTS, new ResourceSetImpl());
        return ocl.parse(uri);
    }

    private ASResource ecoreToAs(URI uri) throws ParserException {
        ResourceSetImpl rs = new ResourceSetImpl();
        OCL ocl = OCL.newInstance(OCL.NO_PROJECTS, rs);
        Resource resource = rs.getResource(uri, true);
        return ocl.ecore2as(resource);
    }
}
