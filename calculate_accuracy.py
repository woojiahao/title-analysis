from tool.accuracy import get_differences_loop

base_path = 'C:\\Users\\Chill\\Jia Hao\\Data Science Challenge\\updated-datasets'

# Mobile
mobile_path = f'{base_path}\\mobile'
mobile_training_analyzed_path = f'{mobile_path}\\mobile_training_analyzed.csv'
mobile_training_original_path = f'{mobile_path}\\training.csv'
mobile_attributes = [
  'Operating Systems',
  'Features',
  'Network Connections',
  'Memory RAM',
  'Brand',
  'Warranty Period',
  'Storage Capacity',
  'Color Family',
  'Phone Model',
  'Camera',
  'Phone Screen Size'
]
get_differences_loop(mobile_training_analyzed_path, mobile_training_original_path, mobile_attributes)

# Beauty
beauty_path = f'{base_path}\\beauty'
beauty_training_analyzed_path = f'{beauty_path}\\beauty_training_analyzed.csv'
beauty_training_original_path = f'{beauty_path}\\training.csv'
beauty_attributes = [
  'Benefits',
  'Brand',
  'Color_group',
  'Product_texture',
  'Skin_type'
]
get_differences_loop(beauty_training_analyzed_path, beauty_training_original_path, beauty_attributes)

# Fashion
fashion_path = f'{base_path}\\fashion'
fashion_training_analyzed_path = f'{fashion_path}\\fashion_traning_analyzed.csv'
fashion_training_original_path = f'{fashion_path}\\training.csv'
fashion_attributes = [
  'Pattern',
  'Collar Type',
  'Fashion Trend',
  'Clothing Material',
  'Sleeves'
]
get_differences_loop(fashion_training_analyzed_path, fashion_training_original_path, fashion_attributes)
