from collections import defaultdict
import json
from constants import SNV, AMP, DEL, INACTIVE_SNV, Mutation, Fusion

################################################################################
# Data loading functions

def load_index(index_file):
    """Load gene index information from file and return as a dict mapping index to gene name.
    
    Arguments:
    index_file -- path to TSV file containing an index in the first column and the name of the gene
                  represented at that index in the second column
    
    """
    with open(index_file) as f:
        arrs  = [l.split() for l in f]
        return dict((int(arr[0]), arr[1]) for arr in arrs)

def load_ppi_edges(edge_list_file, index2gene):
    """Load PPI edges from file and return as a set of 2-tuples of gene names.
    
    Arguments:
    edge_list_file -- path to TSV file containing edges with a gene index in each of the first
                      two columns
    index2gene -- dictionary mapping gene indices to gene names
                      
    Note that edges are undirected, but each edge is represented as a single tuple in the
    returned set. Thus, to check whether a given pair of proteins interact, one must check
    for the presence of either ordered tuple.
    
    """
    with open(edge_list_file) as f:
        arrs = [l.split() for l in f]
        return set((index2gene[int(arr[0])], index2gene[int(arr[1])]) for arr in arrs)

def load_heat_json(heat_file):
    """Load heat JSON file and return a dict mapping gene names to heat scores and a dict mapping
    names of parameters used to generate the heat scores to their values.
    
    Arguments:
    heat_file -- path to heat JSON file generated by generateHeat.py
    
    """
    with open(heat_file) as f:
        blob = json.load(f)
        return blob["heat"], blob["parameters"]

def load_heat_tsv(heat_file):
    """Load scores from a file and return a dict mapping gene names to heat scores.
    
    Arguments
    heat_file -- path to TSV file with gene names in the first column and heat scores in the second
    
    """
    with open(heat_file) as f:
        arrs = [l.split() for l in f]
        return dict((arr[0], float(arr[1])) for arr in arrs)

def load_display_score_tsv(d_score_file):
    """Load scores from a file and return a dict mapping gene names to display scores.

    Arguements
    d_score_file -- path to TSV file with gene names in the first column and heat scores in the second

    """
    with open(d_score_file) as f:
        arrs = [l.split() for l in f]
        return dict((arr[0], float(arr[1])) for arr in arrs)

def load_genes(gene_file):
    """Load tested genes from a file and return as a set.
    
    Arguments:
    gene_file -- path to file containing gene names, one per line
    
    """
    with open(gene_file) as f:
        return set(l.strip() for l in f)

def load_gene_lengths(gene_lengths_file):
    """Load gene lengths from a file and return as a dict mapping gene name to gene length.
    
    Arguments:
    gene_lengths_file -- path to TSV file containing gene names in the first column and the length
                         of the gene in base pairs in the second column
    
    """
    with open(gene_lengths_file) as f:
        arrs = [l.split() for l in f]
        return dict((arr[0], int(arr[1])) for arr in arrs)

def load_gene_order(gene_order_file):
    """Load gene order file and return gene->chromosome and chromosome->ordered gene list mappings.
    
    Arguments:
    gene_order_file -- path to file containing tab-separated lists of genes on each chromosme,
                       one chromosome per line
    
    Note that numeric chromosome identifier used is simply the line number for the chromosome in
    the given file and does not indicate the true chromosome number.
    
    """
    chromo2genes = {}
    gene2chromo = {}
    
    cid = 0
    with open(gene_order_file) as f:
        for line in f:
            genes = line.split()
            chromo2genes[cid] = genes
            gene2chromo.update((gene, cid) for gene in genes)
            cid += 1
        
    return gene2chromo, chromo2genes

def load_gene_specific_bmrs(bmr_file):
    """Load gene BMR information from a file and return as a dict mapping gene name to BMR for the gene.
    
    Arguments:
    bmr_file -- path to TSV file with gene names in the first column and the background mutation rate
                for the gene in the second column
    
    """
    with open(bmr_file) as f:
        arrs = [l.split() for l in f]
        return dict((arr[0], float(arr[1])) for arr in arrs)  

def load_samples(sample_file):
    """Load sample IDs from a file and return as a set.
    
    Arguments:
    sample_file -- path to TSV file containing sample IDs as the first column. Any other columns
                   will be ignored
    
    """
    with open(sample_file) as f:
        return set(l.rstrip().split()[0] for l in f)

def include(item, whitelist):
    return item in whitelist if whitelist else True

def load_snvs(snv_file, gene_wlst=None, sample_wlst=None):
    """Load SNV data from a file and return as a list of Mutation tuples with mut_type == SNV.
 
    Arguments:
    snv_file -- path to TSV file containing SNVs where the first column of each line is a sample ID
                and subsequent columns contain the names of SNVs with mutations in that sample.
                Lines starting with "#" will be ignored.
    gene_wlist -- whitelist of allowed genes (default None). Genes not in this list will be ignored.
                  If None, all mutated genes will be included.
    sample_wlist -- whitelist of allowed samples (default None). Samples not in this list will be
                    ignored.  If None, all samples will be included.

    """
    with open(snv_file) as f:
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
        return [Mutation(arr[0], gene, SNV) for arr in arrs if include(arr[0], sample_wlst)
                for gene in arr[1:] if include(gene, gene_wlst)]

def load_inactivating_snvs(inactivating_snvs_file, gene_wlst=None, sample_wlst=None):
    """Load inactivating SNVs from a file and return as a list of Mutation tuples with
    mut_type == INACTIVE_SNV.
 
    Arguments:
    inactivating_snvs_file -- path to TSV file listing inactivating SNVs where the first column of
                              each line is a gene name and the second column is a sample ID.
                              Lines starting with "#" will be ignored.
    gene_wlist -- whitelist of allowed genes (default None). Genes not in this list will be ignored.
                  If None, all mutated genes will be included.
    sample_wlist -- whitelist of allowed samples (default None). Samples not in this list will be
                    ignored.  If None, all samples will be included.

    """
    with open(inactivating_snvs_file) as f:
        arrs = [line.split() for line in f if not line.startswith("#")]
        return [Mutation(arr[1], arr[0], INACTIVE_SNV)
                for arr in arrs if include(arr[1], sample_wlst) and include(arr[0], gene_wlst)]

def load_cnas(cna_file, gene_wlst=None, sample_wlst=None):
    """Load CNA data from a file and return as a list of Mutation tuples with mut_type == AMP or DEL.
 
    Arguments:
    cna_file -- path to TSV file containing CNAs where the first column of each line is a sample ID
                and subsequent columns contain gene names followed by "(A)" or "(D)" indicating an
                ammplification or deletion in that gene for the sample. Lines starting with '#'
                will be ignored.
    gene_wlist -- whitelist of allowed genes (default None). Genes not in this list will be ignored.
                  If None, all mutated genes will be included.
    sample_wlist -- whitelist of allowed samples (default None). Samples not in this list will be
                    ignored.  If None, all samples will be included.

    """
    with open(cna_file) as f:
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
        return [Mutation(arr[0], cna.split("(")[0], get_mut_type(cna))
                for arr in arrs if include(arr[0], sample_wlst)
                for cna in arr[1:] if include(cna.split("(")[0], gene_wlst)]

def load_fusions(fusion_file, gene_wlst=None, sample_wlst=None, ):
    """Load fusion information from a file and return as a list of Fusion objects.
    
    Arguments:
    fusion_file -- path to TSV file containing a sample ID in the first column and gene names in
                   the second two columns of each line. Lines starting with "#" will be ignored.
    gene_wlist -- whitelist of allowed genes (default None). Genes not in this list will be ignored.
                  If None, all mutated genes will be included. If only one gene of a fusion is in
                  the allowed whitelist, an exception is raised.
    sample_wlist -- whitelist of allowed samples (default None). Samples not in this list will be
                    ignored.  If None, all samples will be included.
    """
    with open(fusion_file) as f:
        arrs = [line.split() for line in f if not line.startswith("#")]
        return [Fusion(arr[0], (arr[1], arr[2])) for arr in arrs
                if include_fusion(sample_wlst, gene_wlst, *arr[:4])]

def include_fusion(sample_wlst, gene_wlst, sample, gene1, gene2):
    if sample_wlst and sample not in sample_wlst: return False
    if not gene_wlst: return True
    if gene1 not in gene_wlst and gene2 not in gene_wlst: return False
    elif (gene1 in gene_wlst and not gene2 in gene_wlst) or \
         (gene2 in gene_wlst and not gene1 in gene_wlst):
        raise ValueError('Genes %s and %s are in a fusion, but one is disallowed by the gene\
                          whitelist' % (gene1, gene2))
    return True 

def load_sample_types(type_file):
    """Load sample type information from a file and return as a dict mapping sample ID to type string
    
    Arguments:
    type_file -- Path to tab-separated file listing sample types where the first column of each
                 line is a sample ID and the second column is a type.
    """
    with open(type_file) as f:
        arrs = [line.split() for line in f]
        return dict((arr[0], arr[1]) for arr in arrs)

def get_mut_type(cna):
    if cna.endswith("(A)"): return AMP
    elif cna.endswith("(D)"): return DEL
    else: raise ValueError("Unknown CNA type in '%s'", cna)

def load_oncodrive_data(fm_scores, cis_amp_scores, cis_del_scores):
    print "* Loading oncodrive data..."
    # Create defaultdicts to hold the fm and cis scores
    one = lambda: 1
    gene2fm = defaultdict(one)
    gene2cis_amp, gene2cis_del = defaultdict(one), defaultdict(one)
    
    # Load fm scores (pvals, not z-scores)
    with open(fm_scores) as f:
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
    gene2fm.update((arr[1], float(arr[2])) for arr in arrs
                   if arr[2] != "" and arr[2] != "-0" and arr[2] != "-")
    print "\tFM genes:", len(gene2fm.keys())

    # Load amplifications
    with open(cis_amp_scores) as f:
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
    gene2cis_amp.update((arr[0], float(arr[-1])) for arr in arrs)
    print "\tCIS AMP genes:", len(gene2cis_amp.keys())

    # Load deletions
    with open(cis_del_scores) as f:
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
    gene2cis_del.update((arr[0], float(arr[-1])) for arr in arrs)
    print "\tCIS DEL genes:", len(gene2cis_del.keys())
    
    # Merge data
    genes = set(gene2cis_del.keys()) | set(gene2cis_amp.keys()) | set(gene2fm.keys())
    print "\t- No. genes:", len(genes)
    gene2heat = dict()
    for g in genes:
        gene2heat[g] = {"del": gene2cis_del[g], "amp": gene2cis_amp[g],
                        "fm": gene2fm[g] }

    return gene2heat

def load_mutsig_scores(scores_file):
    with open(scores_file) as f:
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
        print "* Loading MutSig scores in", len(arrs), "genes..."
        return dict((arr[0], {"pval": float(arr[-2]), "qval": float(arr[-1])})
                    for arr in arrs)


FDR_CT, FDR_LRT, FDR_FCPT = 12, 11, 10
music_score2name = {FDR_CT: "FDR_CT", FDR_LRT: "FDR_LRT", FDR_FCPT: "FDR_FCPT"}
def load_music_scores(scores_file):
    print "* Loading MuSiC scores using the median of the 3 q-values..."
    
    with open(scores_file) as f:
        # Load file and tab-split lines 
        arrs = [l.rstrip().split("\t") for l in f if not l.startswith("#")]
    
        # Indices for the columns we may be interested in
        gene2music = dict((arr[0], {"FDR_CT": float(arr[FDR_CT]),
                                    "FDR_FCPT": float(arr[FDR_FCPT]),
                                    "FDR_LRT":float(arr[FDR_LRT])})
                          for arr in arrs)
    
        # Output parsing info
        print "\t- Loaded %s genes." % len(gene2music)
        return gene2music

################################################################################
# Data saving functions

def write_components_as_tsv(output_file, ccs):
    """Save connected components to file where each line represents a connected component and genes
    within each CC are delimited by tabs.
    
    Arguments:
    output_file -- path to which the output file should be written
    ccs -- list of lists of gene names representing connected components
    
    """
    with open(output_file, 'w') as out_f:
        for cc in ccs:
            out_f.write('\t'.join(cc) + '\n')
            
def write_significance_as_tsv(output_file, sizes2stats):
    """Save significance information to tab-separated file.
    
    Arguments:
    output_file -- path to which the output file should be written
    sizes2stats -- dict mapping a CC size to a dict with the expected number of CCs of at least
                   that size based on permuted data, the observed number of CCs of at least that
                   size in the real data, and the p-value for the observed number
    
    """
    with open(output_file, 'w') as out_f:
        out_f.write("Size\tExpected\tActual\tp-value\n")
        for size, stats in sizes2stats.iteritems():
            out_f.write("%s\t%s\t%s\t%s\n" % (size, stats["expected"], stats["observed"], stats["pval"]))

def write_gene_list(output_file, genelist):
    """Save a list of genes to a file, one gene per line.
    
    Arguments:
    output_file -- path to which the output file should be written
    genelist -- iterable of genes that should be included in the output file
    
    """
    with open(output_file, 'w') as out_f:
        for gene in genelist:
            out_f.write(gene+'\n')


def load_file(file_path):
    with open(file_path) as f:
        return f.read()

def write_file(file_path, text):
    with open(file_path, 'w') as f:
        f.write(text)
    f.close()