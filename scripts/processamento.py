from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum

spark = SparkSession.builder \
    .appName("ProcessamentoResiduos") \
    .getOrCreate()

# 1. Tentaremos ler com UTF-8 (padrão) que parece ser o caso pelo log
# Mantenha a leitura em UTF-8 (que provou funcionar agora)
df = spark.read.option("header", "true") \
               .option("sep", ";") \
               .option("inferSchema", "true") \
               .option("encoding", "UTF-8") \
               .csv("/dados/bruto/residuos.csv")

# Use os nomes em português normal (como aparecem no seu log agora)
df_limpo = df.select(
    col("Município Declarante").alias("municipio"),
    col("UF Declarante").alias("uf"),
    col("orr_descricao").alias("tipo_residuo"),
    col("Caracterização - Descrição").alias("categoria"),
    col("Massa (TON)").cast("double").alias("toneladas")
).na.fill(0, ["toneladas"])

# 2. Vamos listar as colunas no log para você conferir se falhar de novo
print("Colunas encontradas no arquivo:", df.columns)

# 3. Use os nomes EXATOS que o Spark sugeriu no erro para não ter erro de 'Unresolved Column'



df_agrupado = df_limpo.groupBy("municipio", "uf", "categoria") \
                      .agg(_sum("toneladas").alias("total_toneladas")) \
                      .filter(col("categoria").isNotNull())

df_agrupado.coalesce(1) \
           .write \
           .mode("overwrite") \
           .option("header", "true") \
           .csv("/dados/processado/resultado_residuos")

spark.stop()
