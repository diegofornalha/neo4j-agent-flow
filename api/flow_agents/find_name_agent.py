"""
.find Name Service Agent - Agente Flow nativo para gerenciar nomes .find
Integração completa com o name service da Flow blockchain
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

class FindNameServiceAgent:
    """
    Agente autônomo para gerenciar .find names na Flow
    """

    # Endereços dos contratos .find
    FIND_CONTRACTS = {
        "mainnet": {
            "FIND": "0x097bafa4e0b48eef",
            "Profile": "0x097bafa4e0b48eef"
        },
        "testnet": {
            "FIND": "0x35717efbbce11c74",
            "Profile": "0x35717efbbce11c74"
        }
    }

    def __init__(self, network: str = "testnet"):
        self.network = network
        self.contracts = self.FIND_CONTRACTS[network]

    # ===================================
    # REGISTRO DE NOMES
    # ===================================

    def register_name_script(self, name: str, amount: float = 5.0) -> str:
        """
        Gera script Cadence para registrar um nome .find

        Args:
            name: Nome a registrar (sem .find)
            amount: FLOW tokens para pagamento
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import FUSD from 0x3c5959b568896393
        import FungibleToken from 0x9a0766d93b6608b7
        import FlowToken from 0x7e60df042a9c0868

        transaction(name: String, amount: UFix64) {{
            let vault: @FUSD.Vault

            prepare(account: AuthAccount) {{
                // Prepara vault FUSD para pagamento
                let fusdVault = account.borrow<&FUSD.Vault>(from: /storage/fusdVault)
                    ?? panic("Não encontrou FUSD vault")

                self.vault <- fusdVault.withdraw(amount: amount) as! @FUSD.Vault

                // Registra o nome
                FIND.deposit(
                    name: name,
                    vault: <- self.vault
                )
            }}

            execute {{
                log("Nome registrado com sucesso: ".concat(name).concat(".find"))
            }}
        }}
        '''

    def register_quiz_name(self, participant: str, bootcamp_id: str) -> str:
        """
        Registra nome especial para participante do Quiz
        Ex: joao-bootcamp2024.find
        """
        name = f"{participant}-{bootcamp_id}"

        return f'''
        import FIND from {self.contracts["FIND"]}
        import FlowToken from 0x7e60df042a9c0868

        transaction(participant: String, bootcampId: String) {{
            prepare(signer: AuthAccount) {{
                // Nome especial do bootcamp
                let quizName = participant.concat("-").concat(bootcampId)

                // Registra com desconto especial para bootcamp
                FIND.registerBootcampName(
                    name: quizName,
                    participant: signer.address
                )
            }}

            execute {{
                log("Quiz participant registered!")
            }}
        }}
        '''

    # ===================================
    # RESOLUÇÃO DE NOMES
    # ===================================

    def resolve_name_script(self, name: str) -> str:
        """
        Resolve nome .find para endereço Flow
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub fun main(name: String): Address? {{
            // Remove .find se incluído
            let cleanName = name.replacingOccurrences(of: ".find", with: "")
            return FIND.lookupAddress(cleanName)
        }}
        '''

    def reverse_lookup_script(self, address: str) -> str:
        """
        Busca nome .find a partir de endereço
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub fun main(address: Address): String? {{
            if let name = FIND.reverseLookup(address) {{
                return name.concat(".find")
            }}
            return nil
        }}
        '''

    def batch_resolve_script(self, names: List[str]) -> str:
        """
        Resolve múltiplos nomes de uma vez
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub fun main(names: [String]): {{String: Address?}} {{
            let results: {{String: Address?}} = {{}}

            for name in names {{
                let cleanName = name.replacingOccurrences(of: ".find", with: "")
                results[name] = FIND.lookupAddress(cleanName)
            }}

            return results
        }}
        '''

    # ===================================
    # PERFIS .FIND
    # ===================================

    def get_profile_script(self, name: str) -> str:
        """
        Obtém perfil completo de usuário .find
        """
        return f'''
        import FIND, Profile from {self.contracts["FIND"]}

        pub fun main(name: String): Profile.UserProfile? {{
            return FIND.lookup(name)?.asProfile()
        }}
        '''

    def update_profile_transaction(self, bio: str, avatar: str, links: Dict) -> str:
        """
        Atualiza perfil do usuário .find
        """
        return f'''
        import FIND, Profile from {self.contracts["FIND"]}

        transaction(bio: String, avatar: String, links: {{String: String}}) {{
            prepare(account: AuthAccount) {{
                let profile = account.borrow<&Profile.User>(from: /storage/findProfile)
                    ?? panic("Perfil não encontrado")

                profile.setBio(bio)
                profile.setAvatar(avatar)

                for key in links.keys {{
                    profile.addLink(key: key, url: links[key]!)
                }}
            }}
        }}
        '''

    # ===================================
    # QUIZ RACE INTEGRATION
    # ===================================

    def verify_quiz_eligibility_script(self, address: str) -> str:
        """
        Verifica se endereço tem nome .find válido para o quiz
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub fun main(address: Address): Bool {{
            // Verifica se tem nome .find
            if let name = FIND.reverseLookup(address) {{
                // Verifica se é nome de bootcamp
                if name.contains("bootcamp") || name.contains("quiz") {{
                    return true
                }}
                // Qualquer nome .find vale como ticket
                return true
            }}
            return false
        }}
        '''

    def mint_quiz_badge_to_find_name(self, name: str, position: int, prize: float) -> str:
        """
        Adiciona badge de vencedor ao perfil .find
        """
        return f'''
        import FIND, Profile from {self.contracts["FIND"]}
        import QuizRace from 0x01cf0e2f2f715450

        transaction(winnerName: String, position: UInt8, prize: UFix64) {{
            prepare(signer: AuthAccount) {{
                // Busca perfil do vencedor
                let profile = FIND.lookup(winnerName)?.asProfile()
                    ?? panic("Perfil não encontrado")

                // Adiciona badge de vitória
                let badge = QuizRace.WinnerBadge(
                    name: winnerName,
                    position: position,
                    prize: prize,
                    timestamp: getCurrentBlock().timestamp
                )

                // Salva no perfil
                profile.addBadge("quiz_winner_2024", badge)
            }}

            execute {{
                log("Badge adicionado ao perfil .find!")
            }}
        }}
        '''

    # ===================================
    # TRADING & MARKETPLACE
    # ===================================

    def list_name_for_sale_transaction(self, name: str, price: float) -> str:
        """
        Lista nome .find para venda
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import FungibleToken from 0x9a0766d93b6608b7
        import FlowToken from 0x7e60df042a9c0868

        transaction(name: String, price: UFix64) {{
            prepare(account: AuthAccount) {{
                let lease = account.borrow<&FIND.Lease>(from: /storage/findLease)
                    ?? panic("Lease não encontrado")

                // Lista para venda
                lease.listForSale(
                    name: name,
                    price: price,
                    paymentType: Type<@FlowToken.Vault>()
                )
            }}

            execute {{
                log("Nome listado para venda: ".concat(name))
            }}
        }}
        '''

    def buy_name_transaction(self, name: str, amount: float) -> str:
        """
        Compra nome .find listado
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import FlowToken from 0x7e60df042a9c0868
        import FungibleToken from 0x9a0766d93b6608b7

        transaction(name: String, amount: UFix64) {{
            let vault: @FungibleToken.Vault

            prepare(buyer: AuthAccount) {{
                // Prepara pagamento
                let flowVault = buyer.borrow<&FlowToken.Vault>(from: /storage/flowTokenVault)
                    ?? panic("Flow vault não encontrado")

                self.vault <- flowVault.withdraw(amount: amount)

                // Compra o nome
                FIND.buyName(
                    name: name,
                    vault: <- self.vault,
                    recipient: buyer.address
                )
            }}

            execute {{
                log("Nome comprado com sucesso!")
            }}
        }}
        '''

    # ===================================
    # UTILIDADES
    # ===================================

    def get_all_names_script(self, address: str) -> str:
        """
        Lista todos os nomes .find de um endereço
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub fun main(address: Address): [String] {{
            return FIND.getAllNames(address)
        }}
        '''

    def search_names_script(self, pattern: str) -> str:
        """
        Busca nomes por padrão
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub fun main(pattern: String): [String] {{
            // Busca nomes que contenham o padrão
            return FIND.searchNames(pattern: pattern, maxResults: 100)
        }}
        '''

    def get_name_details_script(self, name: str) -> str:
        """
        Detalhes completos de um nome
        """
        return f'''
        import FIND from {self.contracts["FIND"]}

        pub struct NameDetails {{
            pub let name: String
            pub let owner: Address?
            pub let validUntil: UFix64?
            pub let forSale: Bool
            pub let price: UFix64?
            pub let profile: Profile.UserProfile?

            init(
                name: String,
                owner: Address?,
                validUntil: UFix64?,
                forSale: Bool,
                price: UFix64?,
                profile: Profile.UserProfile?
            ) {{
                self.name = name
                self.owner = owner
                self.validUntil = validUntil
                self.forSale = forSale
                self.price = price
                self.profile = profile
            }}
        }}

        pub fun main(name: String): NameDetails {{
            let lease = FIND.getLease(name)

            return NameDetails(
                name: name,
                owner: lease?.owner,
                validUntil: lease?.validUntil,
                forSale: lease?.salePrice != nil,
                price: lease?.salePrice,
                profile: FIND.lookup(name)?.asProfile()
            )
        }}
        '''

    # ===================================
    # QUIZ RACE COM .FIND NAMES
    # ===================================

    def create_quiz_with_find_requirement(self) -> str:
        """
        Cria quiz que requer nome .find para participar
        """
        return f'''
        import FIND from {self.contracts["FIND"]}
        import QuizRace from 0x01cf0e2f2f715450

        pub contract QuizWithFind {{

            pub event QuizStarted(requiredNamePattern: String?)
            pub event ParticipantJoined(name: String, address: Address)
            pub event InvalidName(address: Address, reason: String)

            pub fun startQuiz(requiredPattern: String?) {{
                emit QuizStarted(requiredNamePattern: requiredPattern)
            }}

            pub fun joinQuiz(participant: Address): Bool {{
                // Verifica se tem nome .find
                if let name = FIND.reverseLookup(participant) {{

                    // Se tem padrão específico (ex: deve conter "bootcamp")
                    if let pattern = requiredPattern {{
                        if !name.contains(pattern) {{
                            emit InvalidName(
                                address: participant,
                                reason: "Nome não contém: ".concat(pattern)
                            )
                            return false
                        }}
                    }}

                    emit ParticipantJoined(name: name, address: participant)
                    return true
                }}

                emit InvalidName(
                    address: participant,
                    reason: "Precisa de um nome .find"
                )
                return false
            }}

            pub fun getParticipantDisplayName(address: Address): String {{
                if let name = FIND.reverseLookup(address) {{
                    return name.concat(".find")
                }}
                return "0x".concat(address.toString())
            }}
        }}
        '''

# ===================================
# EXEMPLO DE USO
# ===================================

def example_usage():
    """
    Exemplo de como usar o Find Name Service Agent
    """
    agent = FindNameServiceAgent(network="testnet")

    # 1. Registrar nome para participante do bootcamp
    print("=== REGISTRO DE NOME ===")
    register_script = agent.register_quiz_name("joao", "bootcamp2024")
    print(register_script)

    # 2. Resolver nome para endereço
    print("\n=== RESOLVER NOME ===")
    resolve_script = agent.resolve_name_script("joao-bootcamp2024")
    print(resolve_script)

    # 3. Verificar elegibilidade para quiz
    print("\n=== VERIFICAR ELEGIBILIDADE ===")
    eligibility = agent.verify_quiz_eligibility_script("0x01cf0e2f2f715450")
    print(eligibility)

    # 4. Buscar perfil
    print("\n=== BUSCAR PERFIL ===")
    profile = agent.get_profile_script("joao-bootcamp2024")
    print(profile)

    # 5. Adicionar badge de vencedor
    print("\n=== BADGE DE VENCEDOR ===")
    badge = agent.mint_quiz_badge_to_find_name("joao-bootcamp2024", 1, 300.0)
    print(badge)

if __name__ == "__main__":
    example_usage()