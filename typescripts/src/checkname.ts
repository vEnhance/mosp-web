import Swal from 'sweetalert2';
import { setCookie, deleteCookie } from './cookie';
declare const token_uuid : string | null;

const animals = [
  'Canidae', 'Felidae', 'Cat', 'Cattle', 'Dog', 'Donkey', 'Goat', 'Guinea pig',
  'Horse', 'Pig', 'Rabbit', 'Aardvark', 'Aardwolf', 'African buffalo',
  'African elephant', 'African leopard', 'Albatross', 'Alligator', 'Alpaca',
  'American robin', 'Amphibian', 'Anaconda', 'Angelfish', 'Anglerfish', 'Ant',
  'Anteater', 'Antelope', 'Antlion', 'Ape', 'Aphid', 'Arabian leopard',
  'Arctic Fox', 'Arctic Wolf', 'Armadillo', 'Arrow crab', 'Asp', 'Baboon',
  'Badger', 'Bald eagle', 'Bandicoot', 'Barnacle', 'Barracuda', 'Basilisk',
  'Bass', 'Bat', 'Beaked whale', 'Bear', 'Beaver', 'Bedbug', 'Bee', 'Beetle',
  'Bird', 'Bison', 'Blackbird', 'Black panther', 'Black widow spider',
  'Blue bird', 'Blue jay', 'Blue whale', 'Boa', 'Boar', 'Bobcat', 'Bobolink',
  'Bonobo', 'Booby', 'Box jellyfish', 'Bovid', 'Bug', 'Butterfly', 'Buzzard',
  'Camel', 'Canid', 'Cape buffalo', 'Capybara', 'Cardinal', 'Caribou', 'Carp',
  'Cat', 'Catshark', 'Caterpillar', 'Catfish', 'Cattle', 'Centipede',
  'Cephalopod', 'Chameleon', 'Cheetah', 'Chickadee', 'Chicken', 'Chimpanzee',
  'Chinchilla', 'Chipmunk', 'Clam', 'Clownfish', 'Cobra', 'Cockroach', 'Cod',
  'Condor', 'Constrictor', 'Coral', 'Cougar', 'Cow', 'Coyote', 'Crab', 'Crane',
  'Crane fly', 'Crawdad', 'Crayfish', 'Cricket', 'Crocodile', 'Crow', 'Cuckoo',
  'Cicada', 'Damselfly', 'Deer', 'Dingo', 'Dinosaur', 'Dog', 'Dolphin',
  'Donkey', 'Dormouse', 'Dove', 'Dragonfly', 'Dragon', 'Duck', 'Dung beetle',
  'Eagle', 'Earthworm', 'Earwig', 'Echidna', 'Eel', 'Egret', 'Elephant',
  'Elephant seal', 'Elk', 'Emu', 'English pointer', 'Ermine', 'Falcon',
  'Ferret', 'Finch', 'Firefly', 'Fish', 'Flamingo', 'Flea', 'Fly', 'Flyingfish',
  'Fowl', 'Fox', 'Frog', 'Fruit bat', 'Gamefowl', 'Galliform', 'Gazelle',
  'Gecko', 'Gerbil', 'Giant panda', 'Giant squid', 'Gibbon', 'Gila monster',
  'Giraffe', 'Goat', 'Goldfish', 'Goose', 'Gopher', 'Gorilla', 'Grasshopper',
  'Great blue heron', 'Great white shark', 'Grizzly bear', 'Ground shark',
  'Ground sloth', 'Grouse', 'Guan', 'Guanaco', 'Guineafowl', 'Guinea pig',
  'Gull', 'Guppy', 'Haddock', 'Halibut', 'Hammerhead shark', 'Hamster', 'Hare',
  'Harrier', 'Hawk', 'Hedgehog', 'Hermit crab', 'Heron', 'Herring',
  'Hippopotamus', 'Hookworm', 'Hornet', 'Horse', 'Hoverfly', 'Hummingbird',
  'Humpback whale', 'Hyena', 'Iguana', 'Impala', 'Irukandji jellyfish',
  'Jackal', 'Jaguar', 'Jay', 'Jellyfish', 'Junglefowl', 'Kangaroo',
  'Kangaroo mouse', 'Kangaroo rat', 'Kingfisher', 'Kite', 'Kiwi', 'Koala',
  'Koi', 'Komodo dragon', 'Krill', 'Ladybug', 'Lamprey', 'Landfowl',
  'Land snail', 'Lark', 'Leech', 'Lemming', 'Lemur', 'Leopard', 'Leopon',
  'Limpet', 'Lion', 'Lizard', 'Llama', 'Lobster', 'Locust', 'Loon', 'Louse',
  'Lungfish', 'Lynx', 'Macaw', 'Mackerel', 'Magpie', 'Mammal', 'Manatee',
  'Mandrill', 'Manta ray', 'Marlin', 'Marmoset', 'Marmot', 'Marsupial',
  'Marten', 'Mastodon', 'Meadowlark', 'Meerkat', 'Mink', 'Minnow', 'Mite',
  'Mockingbird', 'Mole', 'Mollusk', 'Mongoose', 'Monitor lizard', 'Monkey',
  'Moose', 'Mosquito', 'Moth', 'Mountain goat', 'Mouse', 'Mule', 'Muskox',
  'Narwhal', 'Newt', 'New World quail', 'Nightingale', 'Ocelot', 'Octopus',
  'Old World quail', 'Opossum', 'Orangutan', 'Orca', 'Ostrich', 'Otter', 'Owl',
  'Ox', 'Panda', 'Panther', 'Panthera hybrid', 'Parakeet', 'Parrot',
  'Parrotfish', 'Partridge', 'Peacock', 'Peafowl', 'Pelican', 'Penguin',
  'Perch', 'Peregrine falcon', 'Pheasant', 'Pig', 'Pigeon', 'Pike',
  'Pilot whale', 'Pinniped', 'Piranha', 'Planarian', 'Platypus', 'Polar bear',
  'Pony', 'Porcupine', 'Porpoise', 'Possum', 'Prairie dog', 'Prawn',
  'Praying mantis', 'Primate', 'Ptarmigan', 'Puffin', 'Puma', 'Python', 'Quail',
  'Quelea', 'Quokka', 'Rabbit', 'Raccoon', 'Rainbow trout', 'Rat',
  'Rattlesnake', 'Raven', 'Red panda', 'Reindeer', 'Reptile', 'Rhinoceros',
  'Right whale', 'Roadrunner', 'Rodent', 'Rook', 'Rooster', 'Roundworm',
  'Saber-toothed cat', 'Sailfish', 'Salamander', 'Salmon', 'Sawfish',
  'Scale insect', 'Scallop', 'Scorpion', 'Seahorse', 'Sea lion', 'Sea slug',
  'Sea snail', 'Shark', 'Sheep', 'Shrew', 'Shrimp', 'Silkworm', 'Silverfish',
  'Skink', 'Skunk', 'Sloth', 'Slug', 'Smelt', 'Snail', 'Snake', 'Snipe',
  'Snow leopard', 'Sockeye salmon', 'Sole', 'Sparrow', 'Sperm whale', 'Spider',
  'Spider monkey', 'Spoonbill', 'Squid', 'Squirrel', 'Starfish',
  'Star-nosed mole', 'Steelhead trout', 'Stingray', 'Stoat', 'Stork',
  'Sturgeon', 'Sugar glider', 'Swallow', 'Swan', 'Swift', 'Swordfish',
  'Swordtail', 'Tahr', 'Takin', 'Tapir', 'Tarantula', 'Tarsier',
  'Tasmanian devil', 'Termite', 'Tern', 'Thrush', 'Tick', 'Tiger',
  'Tiger shark', 'Tiglon', 'Toad', 'Tortoise', 'Toucan', 'Trapdoor spider',
  'Tree frog', 'Trout', 'Tuna', 'Turkey', 'Turtle', 'Tyrannosaurus', 'Urial',
  'Vampire bat', 'Vampire squid', 'Vicuna', 'Viper', 'Vole', 'Vulture',
  'Wallaby', 'Walrus', 'Wasp', 'Warbler', 'Water Boa', 'Water buffalo',
  'Weasel', 'Whale', 'Whippet', 'Whitefish', 'Whooping crane', 'Wildcat',
  'Wildebeest', 'Wildfowl', 'Wolf', 'Wolverine', 'Wombat', 'Woodpecker', 'Worm',
  'Wren', 'Xerinae', 'X-ray fish', 'Yak', 'Yellow perch', 'Zebra', 'Zebra finch'];

function randomChoice(arr : string[]) : string {
  return arr[Math.floor(arr.length * Math.random())];
}

function main(
  name: string,
  force_new : boolean,
  passphrase? : string,
) {
  $.post('/ajax', {
    action : 'get_token',
    name : name,
    force_new : force_new,
    passphrase : passphrase || '',
  }, (result) => {
    if (result.outcome === 'success') {
      setCookie('uuid', result.uuid);
      Swal.fire({
        title: `Nice to meet you, ${name}!`,
        text : `Do you want attach your Discord account `
          + `to save your progress across devices `
          + `and access post-solve channels?`,
        icon: 'success',
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No",
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.replace('/accounts/discord/login?process=login');
        } else {
          window.location.reload();
        }
      });
    } else if (result.outcome === 'exists') {
      Swal.fire({
        title: "Do I know you?",
        text: "I remember someone with this name. Is it you?",
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No",
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.replace('/accounts/discord/login/?process=login');
        } else {
          main(name, true); // create new token with this name
        }
      });
    }
  });
}

function getName() {
  Swal.fire({
    title: "Hello hello hey",
    text: "What should I call you?",
    input: 'text',
    icon: 'info',
    confirmButtonText: 'Set name',
  }).then((result) =>  {
    if (result.isConfirmed) {
      const name = (
        result.value
        || "Anonymous " + randomChoice(animals)
      );
      main(name, false);
    }
  });
}

$(() => {
  if (token_uuid === null) {
    getName();
  } else {
    setCookie('uuid', token_uuid);
  }
  $("#cleartoken").on('click', () => {
    deleteCookie('uuid');
  });
});
