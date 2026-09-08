"""Package curated teaching inputs; this is NOT a native OpenMAIC classroom archive."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
FILES=['handbook/14_physical_connections.md','handbook/15_frames_matrices_fk.md','handbook/16_prerequisites_and_deeper_topics.md',
'assessments/FOUNDATION_BRIDGES.md','templates/LEARNING_QUESTION.md','integrations/openmaic/TEACHER_PROMPT.md',
'integrations/openmaic/ACCEPTANCE.md','integrations/openmaic/source_review.json','OPENMAIC.md',
'assets/interactive/concept_player.html','assets/interactive/matrix_product.svg','assets/interactive/frame_coordinates.svg',
'assets/interactive/transform_order.svg','assets/interactive/fk_chain.svg','assets/interactive/uart_sampling.svg',
'assets/interactive/can_physical.svg','assets/interactive/spi_wiring.svg']

def main():
    target=ROOT/'integrations/openmaic/openmaic_pilot_materials.zip'
    records=[]
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in FILES:
            data=(ROOT/name).read_bytes();bundle.writestr(name,data)
            records.append({'path':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
        bundle.writestr('BUNDLE_README.txt','Teaching inputs only, NOT native .maic.zip. Extract and use the prompt and selected lesson content. Relative links to the full course may require the original trainning_materials folder. No credentials, notebooks runtime, mesh libraries or robot data are included.')
        bundle.writestr('MANIFEST.json',json.dumps({'kind':'teaching-materials','native_openmaic_import':False,'files':records},indent=2))
    with zipfile.ZipFile(target) as bundle:
        assert bundle.testzip() is None
        for row in records: assert hashlib.sha256(bundle.read(row['path'])).hexdigest()==row['sha256']
    print('Pilot ZIP:',target.name,len(records),'verified source files')
if __name__=='__main__': main()
