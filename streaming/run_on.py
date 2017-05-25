import luigi

if __name__ == '__main__':
    luigi.run(['GenerateBlitZip', '--input-file', '/blit/Europeana-Collections-1914-1918/jp2s-euid-duid.csv', '--local-scheduler'])

#luigi.run(['GenerateBlitZip', '--input-file', '/blit/Google_DArks_test.csv', '--local-scheduler'])
#luigi.run(['GenerateBlitZip', '--input-file', '/blit/chunks/Google_DArks_ex_alto.csv.chunk00', '--local-scheduler'])
