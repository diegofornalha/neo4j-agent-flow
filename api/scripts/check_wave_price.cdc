import WaveNameService from 0x36395f9dde50ea27

access(all) fun main(name: String, years: UFix64): UFix64 {
    let duration = years * 31536000.0 // segundos em um ano
    return WaveNameService.calculateCost(name, duration)
}