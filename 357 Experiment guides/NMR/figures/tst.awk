BEGIN { min = max = "NaN" }
{
	min = (NR==1 || $1<min ? $1 : min)
	max = (NR==1 || $1>max ? $1 : max)
}
END { print min, max }

