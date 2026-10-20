# Reproducible small-system experiments for Random Quantum Circuits.
# Julia >= 1.10; standard libraries only. Site 1 is the least significant bit.
using LinearAlgebra, Random, Statistics, Printf, Test
BLAS.set_num_threads(1)

"Haar U(d) from complex Gaussian QR, with diagonal phase correction."
function haar(rng, d=4)
    z = (randn(rng, d, d) + im * randn(rng, d, d)) / sqrt(2)
    f = qr(z)
    phases = [iszero(f.R[k,k]) ? 1.0 + 0im : f.R[k,k] / abs(f.R[k,k]) for k in 1:d]
    return Matrix(f.Q) * Diagonal(phases)
end

"Apply a two-site gate to adjacent sites j,j+1, in local order 00,10,01,11."
function gate!(psi, u, j)
    bit = 1 << (j-1)
    mask = bit | (bit << 1)
    for base in 0:length(psi)-1
        (base & mask) == 0 || continue
        ids = (base+1, base+bit+1, base+2bit+1, base+3bit+1)
        v = u * ComplexF64[psi[k] for k in ids]
        for a in 1:4
            psi[ids[a]] = v[a]
        end
    end
    return psi
end

"Born-sample a projective Z measurement; return outcome and its probability."
function measure!(rng, psi, j)
    bit = 1 << (j-1)
    p0 = clamp(sum(abs2(psi[k+1]) for k in 0:length(psi)-1 if (k & bit) == 0), 0, 1)
    outcome = rand(rng) < p0 ? 0 : 1
    prob = outcome == 0 ? p0 : 1-p0
    prob > 0 || error("sampled a zero-probability measurement")
    for k in 0:length(psi)-1
        psi[k+1] = ((k & bit) == 0) == (outcome == 0) ? psi[k+1]/sqrt(prob) : 0
    end
    return outcome, prob
end

"Entropies of the first ell sites; singular values squared are Schmidt weights."
function entropies(psi, ell)
    weights = abs2.(svdvals(reshape(psi, 1 << ell, :)))
    weights ./= sum(weights)
    s1 = -sum(w * log(w) for w in weights if w > 0)
    s2 = -log(sum(abs2, weights))
    return s1, s2
end

"A trajectory sampled just AFTER each layer's measurements."
function trajectory(rng; L=8, T=32, p=0.0)
    psi = zeros(ComplexF64, 1 << L)
    psi[1] = 1
    values = zeros(T+1, 2)
    for t in 1:T
        firstsite = isodd(t) ? 1 : 2
        for j in firstsite:2:L-1
            gate!(psi, haar(rng), j)
        end
        for j in 1:L
            rand(rng) < p && measure!(rng, psi, j)
        end
        @assert isapprox(norm(psi), 1; atol=2e-12)
        values[t+1, :] .= entropies(psi, L ÷ 2)
    end
    return values
end

function selfcheck()
    @testset "Circuit physics and tensor conventions" begin
        rng = MersenneTwister(53719)
        u = haar(rng)
        @test u' * u ≈ Matrix{ComplexF64}(I,4,4)
        # Bell pair |00>+|11>, including site order and conditional collapse.
        bell = ComplexF64[1,0,0,1] / sqrt(2)
        @test entropies(bell, 1)[1] ≈ log(2)
        @test entropies(bell, 1)[2] ≈ log(2)
        psi = ComplexF64[1,0,0,0]
        h = ComplexF64[1 1; 1 -1] / sqrt(2)
        # Control first (least significant) site; swaps local indices 10 <-> 11.
        cnot = ComplexF64[1 0 0 0; 0 0 0 1; 0 0 1 0; 0 1 0 0]
        gate!(psi, kron(Matrix{ComplexF64}(I,2,2), h), 1)
        gate!(psi, cnot, 1)
        @test psi ≈ bell
        _, prob = measure!(rng, psi, 1)
        @test prob ≈ 0.5
        @test norm(psi) ≈ 1
        @test abs(entropies(psi,1)[1]) < 1e-12
        # Compare bitwise application with an independently assembled tensor product.
        state = randn(rng, ComplexF64, 16); state ./= norm(state)
        explicit = kron(Matrix{ComplexF64}(I,2,2), u, Matrix{ComplexF64}(I,2,2)) * state
        @test gate!(copy(state),u,2) ≈ explicit
        # Measure all sites: every trajectory ends in a computational product state.
        @test maximum(abs, trajectory(rng; L=6,T=5,p=1.0)) < 1e-11
        # Average two-qubit Haar purity for a product input is exactly 4/5.
        purities = [sum(abs2, abs2.(svdvals(reshape(haar(rng)[:,1],2,2)))) for _ in 1:12000]
        @test abs(mean(purities)-0.8) < 6std(purities)/sqrt(length(purities))
    end
end

function main()
    selfcheck()
    L, T, samples = 8, 32, 128
    outdir = joinpath(@__DIR__, "..", "data")
    mkpath(outdir)
    open(joinpath(outdir,"entanglement.csv"),"w") do io
        println(io,"L,layers,p,samples,seed,S1_mean,S1_se,S2_mean,S2_se,annealed_S2")
        for (i,p) in enumerate((0.0,0.15,0.6,1.0))
            seed = 20261020+i
            rng = MersenneTwister(seed)
            draws = cat([trajectory(rng; L,T,p) for _ in 1:samples]...; dims=3)
            for t in 0:T
                s1, s2 = draws[t+1,1,:], draws[t+1,2,:]
                annealed = -log(mean(exp.(-s2)))
                @printf(io,"%d,%d,%.2f,%d,%d,%.12g,%.12g,%.12g,%.12g,%.12g\n",
                    L,t,p,samples,seed,mean(s1),std(s1)/sqrt(samples),mean(s2),std(s2)/sqrt(samples),annealed)
            end
        end
    end
    println("Wrote data/entanglement.csv (L=8, 32 layers, 128 trajectories per p).")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
